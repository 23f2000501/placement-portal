export function getAuth() {
  return {
    user: JSON.parse(localStorage.getItem("user") || "null"),
    token: localStorage.getItem("access_token")
  };
}

export function saveAuth(user, token) {
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("access_token", token);
}

export function logout() {
  localStorage.removeItem("user");
  localStorage.removeItem("access_token");
}