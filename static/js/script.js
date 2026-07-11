// ---------------- SUCCESS ALERT AUTO CLOSE ---------------- //

setTimeout(function () {

    let alerts = document.querySelectorAll(".alert");

    alerts.forEach(function(alert){

        alert.style.transition = "0.5s";

        alert.style.opacity = "0";

        setTimeout(function(){

            alert.remove();

        },500);

    });

},3000);



// ---------------- DELETE CONFIRM ---------------- //

function confirmDelete(){

    return confirm("Are you sure you want to delete this event?");

}



// ---------------- PHONE VALIDATION ---------------- //

function validatePhone(){

    let phoneInput = document.getElementById("phone");

    if(phoneInput){

        let phone = phoneInput.value;

        let regex = /^[0-9]{10}$/;


        if(!regex.test(phone)){

            alert("Enter Valid 10 Digit Phone Number");

            return false;

        }

    }

    return true;

}



// ---------------- PASSWORD MATCH ---------------- //

function checkPassword(){

    let pass = document.getElementById("password");

    let confirmPass = document.getElementById("confirm_password");


    if(pass && confirmPass){

        if(pass.value !== confirmPass.value){

            alert("Passwords do not match");

            return false;

        }

    }

    return true;

}