import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDlSS63rNWem8eev9VV4S0cp9JRsYO84ps",
  authDomain: "parking-app222.firebaseapp.com",
  projectId: "parking-app222",
  appId: "1:563559829034:web:619388086ae2319b1fbd53",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const adminEmails = [
  "admin@parking.com"
];

window.registerUser = function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    // Extra fields (for later DB storage)
    const username = document.getElementById("username").value;
    const fullname = document.getElementById("fullname").value;
    const address = document.getElementById("address").value;
    const pincode = document.getElementById("pincode").value;
  
    createUserWithEmailAndPassword(auth, email, password)
      .then(() => {
        alert("Registration successful!");
        
        // Later you can send these to Flask via fetch()
        console.log(username, fullname, address, pincode);
  
        window.location.href = "/user/login";
      })
      .catch(err => alert(err.message));
  };
  
  
