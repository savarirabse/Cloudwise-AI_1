from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session
from sqlalchemy import func

import json

from app.core.database import get_db
from app.core.security import decode_access_token

from app.models.user import User

from app.models.knowledge import (
    KnowledgePost,
    KnowledgeComment,
    KnowledgeRating
)


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge Hub"]
)

security = HTTPBearer()


# =========================================================
# AUTHENTICATION HELPER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session
):

    try:

        user_id = decode_access_token(
            credentials.credentials
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================================================
# CREATE ARTICLE / QUESTION / SOLUTION
# =========================================================

@router.post("/posts")
def create_post(

    content_type: str,
    title: str,
    content: str,
    category: str,
    tags: list[str] = [],
    
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: Session = Depends(get_db)
):

    user = get_current_user(
        credentials,
        db
    )

    allowed_types = {
        "article",
        "question",
        "solution"
    }

    if content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "content_type must be "
                "article, question or solution"
            )
        )

    if not title.strip():

        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    if not content.strip():

        raise HTTPException(
            status_code=400,
            detail="Content cannot be empty"
        )

    post = KnowledgePost(

        author_id=user.id,

        content_type=content_type,

        title=title.strip(),

        content=content.strip(),

        category=category.strip(),

        tags=json.dumps(tags),

        is_published=True
    )

    db.add(post)

    db.commit()

    db.refresh(post)

    return {

        "message": "Knowledge post created successfully",

        "post": {

            "id": post.id,

            "author_id": post.author_id,

            "content_type": post.content_type,

            "title": post.title,

            "content": post.content,

            "category": post.category,

            "tags": tags,

            "created_at": post.created_at
        }
    }


# =========================================================
# GET ALL POSTS
# =========================================================

@router.get("/posts")
def get_posts(

    content_type: str | None = None,

    search: str | None = None,

    category: str | None = None,

    sort: str = Query(
        "newest",
        pattern="^(newest|oldest|az|za|best-rated|most-rated|most-discussed)$"
    ),

    db: Session = Depends(get_db)
):

    query = (
        db.query(
            KnowledgePost,

            User.first_name,

            User.last_name,

            func.coalesce(
                func.avg(KnowledgeRating.rating),
                0
            ).label("average_rating"),

            func.count(
                func.distinct(
                    KnowledgeRating.id
                )
            ).label("rating_count"),

            func.count(
                func.distinct(
                    KnowledgeComment.id
                )
            ).label("comment_count")
        )
        .join(
            User,
            User.id == KnowledgePost.author_id
        )
        .outerjoin(
            KnowledgeRating,
            KnowledgeRating.post_id == KnowledgePost.id
        )
        .outerjoin(
            KnowledgeComment,
            KnowledgeComment.post_id == KnowledgePost.id
        )
        .filter(
            KnowledgePost.is_published == True
        )
        .group_by(
            KnowledgePost.id,
            User.first_name,
            User.last_name
        )
    )


    # -----------------------------------------------------
    # TYPE FILTER
    # -----------------------------------------------------

    if content_type:

        query = query.filter(
            KnowledgePost.content_type ==
            content_type
        )


    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        query = query.filter(
            KnowledgePost.category ==
            category
        )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        search_pattern = (
            f"%{search.strip()}%"
        )

        query = query.filter(

            KnowledgePost.title.ilike(
                search_pattern
            )

            |

            KnowledgePost.content.ilike(
                search_pattern
            )

            |

            KnowledgePost.category.ilike(
                search_pattern
            )

            |

            KnowledgePost.tags.ilike(
                search_pattern
            )
        )


    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    if sort == "oldest":

        query = query.order_by(
            KnowledgePost.created_at.asc()
        )

    elif sort == "az":

        query = query.order_by(
            KnowledgePost.title.asc()
        )

    elif sort == "za":

        query = query.order_by(
            KnowledgePost.title.desc()
        )

    elif sort == "best-rated":

        query = query.order_by(
            func.avg(
                KnowledgeRating.rating
            ).desc()
        )

    elif sort == "most-rated":

        query = query.order_by(
            func.count(
                func.distinct(
                    KnowledgeRating.id
                )
            ).desc()
        )

    elif sort == "most-discussed":

        query = query.order_by(
            func.count(
                func.distinct(
                    KnowledgeComment.id
                )
            ).desc()
        )

    else:

        query = query.order_by(
            KnowledgePost.created_at.desc()
        )


    results = query.all()

    posts = []


    for (
        post,
        first_name,
        last_name,
        average_rating,
        rating_count,
        comment_count
    ) in results:

        try:

            tags = json.loads(
                post.tags
            )

        except Exception:

            tags = []


        posts.append({

            "id": post.id,

            "content_type":
                post.content_type,

            "title":
                post.title,

            "content":
                post.content,

            "category":
                post.category,

            "tags":
                tags,

            "author": {

                "id":
                    post.author_id,

                "name":
                    f"{first_name} {last_name}".strip()
            },

            "rating":
                round(
                    float(
                        average_rating
                    ),
                    1
                ),

            "rating_count":
                rating_count,

            "comment_count":
                comment_count,

            "created_at":
                post.created_at,

            "updated_at":
                post.updated_at
        })


    return {

        "count":
            len(posts),

        "posts":
            posts
    }


# =========================================================
# GET SINGLE POST
# =========================================================

@router.get("/posts/{post_id}")
def get_post(

    post_id: int,

    db: Session = Depends(get_db)
):

    result = (

        db.query(

            KnowledgePost,

            User.first_name,

            User.last_name,

            func.coalesce(
                func.avg(
                    KnowledgeRating.rating
                ),
                0
            ).label("average_rating"),

            func.count(
                func.distinct(
                    KnowledgeRating.id
                )
            ).label("rating_count"),

            func.count(
                func.distinct(
                    KnowledgeComment.id
                )
            ).label("comment_count")
        )

        .join(
            User,
            User.id == KnowledgePost.author_id
        )

        .outerjoin(
            KnowledgeRating,
            KnowledgeRating.post_id ==
            KnowledgePost.id
        )

        .outerjoin(
            KnowledgeComment,
            KnowledgeComment.post_id ==
            KnowledgePost.id
        )

        .filter(
            KnowledgePost.id == post_id
        )

        .group_by(
            KnowledgePost.id,
            User.first_name,
            User.last_name
        )

        .first()
    )


    if not result:

        raise HTTPException(
            status_code=404,
            detail="Knowledge post not found"
        )


    (
        post,
        first_name,
        last_name,
        average_rating,
        rating_count,
        comment_count
    ) = result


    try:

        tags = json.loads(
            post.tags
        )

    except Exception:

        tags = []


    return {

        "id":
            post.id,

        "content_type":
            post.content_type,

        "title":
            post.title,

        "content":
            post.content,

        "category":
            post.category,

        "tags":
            tags,

        "author": {

            "id":
                post.author_id,

            "name":
                f"{first_name} {last_name}".strip()
        },

        "rating":
            round(
                float(
                    average_rating
                ),
                1
            ),

        "rating_count":
            rating_count,

        "comment_count":
            comment_count,

        "created_at":
            post.created_at,

        "updated_at":
            post.updated_at
    }


# =========================================================
# ADD COMMENT / ANSWER
# =========================================================

@router.post("/posts/{post_id}/comments")
def add_comment(

    post_id: int,

    content: str,

    is_answer: bool = False,

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: Session = Depends(get_db)
):

    user = get_current_user(
        credentials,
        db
    )


    post = (

        db.query(KnowledgePost)

        .filter(
            KnowledgePost.id ==
            post_id
        )

        .first()
    )


    if not post:

        raise HTTPException(
            status_code=404,
            detail="Knowledge post not found"
        )


    if not content.strip():

        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty"
        )


    # Answers only make sense for questions
    if is_answer and post.content_type != "question":

        raise HTTPException(
            status_code=400,
            detail="Answers can only be added to questions"
        )


    comment = KnowledgeComment(

        post_id=post.id,

        author_id=user.id,

        content=content.strip(),

        is_answer=is_answer
    )


    db.add(comment)

    db.commit()

    db.refresh(comment)


    return {

        "message":
            "Comment added successfully",

        "comment": {

            "id":
                comment.id,

            "post_id":
                comment.post_id,

            "author_id":
                comment.author_id,

            "content":
                comment.content,

            "is_answer":
                comment.is_answer,

            "created_at":
                comment.created_at
        }
    }


# =========================================================
# GET COMMENTS / ANSWERS
# =========================================================

@router.get("/posts/{post_id}/comments")
def get_comments(

    post_id: int,

    db: Session = Depends(get_db)
):

    comments = (

        db.query(

            KnowledgeComment,

            User.first_name,

            User.last_name
        )

        .join(
            User,
            User.id ==
            KnowledgeComment.author_id
        )

        .filter(
            KnowledgeComment.post_id ==
            post_id
        )

        .order_by(
            KnowledgeComment.created_at.asc()
        )

        .all()
    )


    return {

        "count":
            len(comments),

        "comments": [

            {

                "id":
                    comment.id,

                "content":
                    comment.content,

                "is_answer":
                    comment.is_answer,

                "author": {

                    "id":
                        comment.author_id,

                    "name":
                        f"{first_name} {last_name}".strip()
                },

                "created_at":
                    comment.created_at
            }

            for (
                comment,
                first_name,
                last_name
            ) in comments
        ]
    }


# =========================================================
# RATE POST
# =========================================================

@router.post("/posts/{post_id}/rating")
def rate_post(

    post_id: int,

    rating: int,

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: Session = Depends(get_db)
):

    user = get_current_user(
        credentials,
        db
    )


    if rating < 1 or rating > 5:

        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )


    post = (

        db.query(KnowledgePost)

        .filter(
            KnowledgePost.id ==
            post_id
        )

        .first()
    )


    if not post:

        raise HTTPException(
            status_code=404,
            detail="Knowledge post not found"
        )


    existing_rating = (

        db.query(KnowledgeRating)

        .filter(
            KnowledgeRating.post_id ==
            post_id,

            KnowledgeRating.user_id ==
            user.id
        )

        .first()
    )


    if existing_rating:

        existing_rating.rating = rating

        message = "Rating updated successfully"

    else:

        new_rating = KnowledgeRating(

            post_id=post_id,

            user_id=user.id,

            rating=rating
        )

        db.add(new_rating)

        message = "Rating submitted successfully"


    db.commit()


    return {

        "message":
            message,

        "rating":
            rating
    }