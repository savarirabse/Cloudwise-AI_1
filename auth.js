const AUTH_TOKEN_KEY = "cloudwise_access_token";
const USER_KEY = "cloudwise_user";


// =====================================================
// GET ACCESS TOKEN
// =====================================================

function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}


// =====================================================
// GET STORED USER
// =====================================================

function getStoredUser() {

    const user = localStorage.getItem(USER_KEY);

    if (!user) {
        return null;
    }

    try {
        return JSON.parse(user);
    } catch (error) {
        console.error("Invalid stored user:", error);
        return null;
    }
}


// =====================================================
// VERIFY CURRENT USER WITH BACKEND
// =====================================================

async function verifyAuthentication() {

    const token = getAuthToken();

    if (!token) {
        return null;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/auth/me",
            {
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + token,
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {

            console.warn(
                "Authentication verification failed:",
                response.status
            );

            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(USER_KEY);

            return null;
        }

        const user = await response.json();

        // Store latest user information
        localStorage.setItem(
            USER_KEY,
            JSON.stringify(user)
        );

        return user;

    } catch (error) {

        console.error(
            "Authentication verification failed:",
            error
        );

        return getStoredUser();
    }
}


// =====================================================
// DISPLAY CURRENT USER
// =====================================================

function displayCurrentUser(user) {

    if (!user) {
        console.warn("No current user available.");
        return;
    }

    const firstName = user.first_name || "User";


    // -------------------------------------------------
    // Sidebar name
    // -------------------------------------------------

    const sidebarUserName =
        document.getElementById("sidebarUserName");

    if (sidebarUserName) {
        sidebarUserName.textContent = firstName;
    }


    // -------------------------------------------------
    // Dashboard greeting
    // -------------------------------------------------

    const dashboardUserName =
        document.getElementById("dashboardUserName");

    if (dashboardUserName) {
        dashboardUserName.textContent = firstName;
    }


    // -------------------------------------------------
    // Avatar
    // -------------------------------------------------

    const userAvatar =
        document.getElementById("userAvatar");

    if (userAvatar) {

        userAvatar.textContent =
            firstName
                .charAt(0)
                .toUpperCase();

    }


    console.log(
        "Current Cloudwise user:",
        firstName
    );
}


// =====================================================
// LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    sessionStorage.clear();

    window.location.href = "login.html";
}


// =====================================================
// PAGE LOAD
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        const token = getAuthToken();

        // No logged-in user
        if (!token) {
            console.log(
                "No Cloudwise login token found."
            );
            return;
        }

        // Get latest user from backend
        const user =
            await verifyAuthentication();

        // Display user
        displayCurrentUser(user);

    }
);