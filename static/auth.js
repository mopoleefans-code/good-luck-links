import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  sendEmailVerification,
  signInWithEmailAndPassword,
    GoogleAuthProvider,
    signInWithPopup,
  reload
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

import firebaseConfig from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

window.registerWithEmail = async function(email, password) {
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    await sendEmailVerification(result.user);
    alert("Verification link sent. Check your email, click the link, then return here and sign in.");
  } catch (error) {
    alert(error.message);
  }
};

window.loginWithEmail = async function(email, password, firstName, secondName) {
  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    await reload(result.user);

    if (!result.user.emailVerified) {
      alert("Your email is not verified yet. Open the verification link in your email first.");
      return;
    }

    const token = await result.user.getIdToken(true);
    const response = await fetch("/auth/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        token,
        first_name: firstName,
        second_name: secondName
      })
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Registration failed.");
    window.location.href = data.redirect;
  } catch (error) {
    alert(error.message);
  }
};


window.loginWithGoogle = async function(firstName, secondName) {
  try {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    const token = await result.user.getIdToken(true);

    const response = await fetch("/auth/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        token,
        first_name: firstName,
        second_name: secondName
      })
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Google sign-in failed.");
    window.location.href = data.redirect;
  } catch (error) {
    alert(error.message);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const getValue = id => document.getElementById(id)?.value.trim() || "";

  document.getElementById("email-login")?.addEventListener("click", () => {
    window.loginWithEmail(
      getValue("login_email"),
      document.getElementById("login_password").value,
      "",
      ""
    );
  });

  document.getElementById("create-account")?.addEventListener("click", () => {
    window.registerWithEmail(
      getValue("email"),
      document.getElementById("password").value
    );
  });

  document.getElementById("google-login")?.addEventListener("click", () => {
    window.loginWithGoogle(getValue("first_name"), getValue("second_name"));
  });

  document.getElementById("verified-login")?.addEventListener("click", () => {
    window.loginWithEmail(
      getValue("email"),
      document.getElementById("password").value,
      getValue("first_name"),
      getValue("second_name")
    );
  });
});
