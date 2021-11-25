//Username
const usernameField = document.querySelector('#username')//pick username console.log(usernameField)
const invalidFeedback = document.querySelector('.invalidFeedback')//display Error as someone types message console.log(invalidFeedback)
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput')//console.log(usernameSuccessOutput)
//Email
const emailField = document.querySelector('#email')//pick email data 
const invalidEmailFeedback = document.querySelector('.invalidEmailFeedback')//console.log(emailField)
const emailSuccessOutput = document.querySelector('.emailSuccessOutput') // console.log(emailSuccessOutput)

//Show PasswordToggle
const showPasswordToggle = document.querySelector('.showPasswordToggle')//

//password
const password = document.querySelector('.password')

//confirmPassword
const confirmPassword = document.querySelector('.confirmPassword')
//pick the button
const registerBtn = document.querySelector('.register')
//compare passwords
const comparePasswod = document.querySelector('.comparePasswod')

    //create the togglePassword function
    const handleToggleInput= (e) => {
        if(showPasswordToggle.textContent==="SHOW"){
            showPasswordToggle.textContent="HIDE"
            password.setAttribute("type","text")
            confirmPassword.setAttribute("type","text")
        }else if(showPasswordToggle.textContent==="HIDE"){
            showPasswordToggle.textContent="SHOW"
            password.setAttribute("type","password")
            confirmPassword.setAttribute("type","password")
        }
    }
    //add a listener to button
    showPasswordToggle.addEventListener("click", handleToggleInput);
    console.log(showPasswordToggle)

    //check confirmPassword password
    confirmPassword.addEventListener('keyup', (e)=>{
        comparePasswod.innerHTML=''
        const confirmPasswordValue = e.target.value//pick value typed in confirmPassword
        if(confirmPasswordValue != password.value){
            registerBtn.disabled = true; //console.log(password.value+'---'+confirmPasswordValue)
            comparePasswod.style.display='block'
            comparePasswod.innerHTML=`<p> Passwords did not match</p>` //display the Error in the div
        }else {
            //console.log(password.value+'---'+confirmPasswordValue)
            registerBtn.disabled = false; 
            comparePasswod.style.display='none'
        }
    })

    //Username validation
    usernameField.addEventListener('keyup', (e)=>{
    //pick what the user has typed
    const usernameValue = e.target.value //console.log(usernameValue)
    usernameSuccessOutput.style.display='block'
    usernameSuccessOutput.textContent = `Checking ${usernameValue} `;

    usernameField.classList.remove("is-invalid");//turns the field red
    invalidFeedback.style.display='none'

    //if the length of what someone is typing is not empty, make the call
    if (usernameValue.length > 0 ){
    //make an AIP call using the fetch API provided by javascript
    //provide it with a url==since we are on the same serve, we are giving it the url in our urls.py file in the authentication app
    //the second argument has what we are receiving in the views.py under UsernameValidationView
    fetch("/authentication/UsernameValidationView",{
        body:JSON.stringify({ username: usernameValue }), // You need to stringify the request data or objects for easy sending over the network
                method:"POST", 
    })//fetch returns a promise , that we need to mapp to JSON
    .then((res) => res.json())//map it to json
    .then((data) => {//this returns another promise that has the data console.log("data",data)
        console.log("data",data)
        usernameSuccessOutput.style.display='none'
        if(data.username_error){// 
            usernameField.classList.add("is-invalid");//turns the field red
            invalidFeedback.style.display='block'
            invalidFeedback.innerHTML=`<p> ${data.username_error}</p>` //display the Error in the div
            registerBtn.disabled = true;   //They basically do the same thing registerBtn.setAttribute('disabled','disabled')
        }
        else{ // Enable the button once the Error is gone
            registerBtn.removeAttribute("disabled")
        }
    });
}
});//close the event listener

// Email Validation
emailField.addEventListener('keyup', (e)=> {
    const emailValue = e.target.value; //console.log(emailValue)
    emailSuccessOutput.style.display='block'
    emailField.classList.remove("is-invalid");//turns the field red
    invalidEmailFeedback.style.display='none'
    emailSuccessOutput.textContent = `Checking ${emailValue} `;

    if (emailValue.length > 0 ){
        fetch("/authentication/EmailValidationView",{
            body:JSON.stringify({ email: emailValue }), // You need to stringify the request data or objects for easy sending over the network
                    method:"POST", 
        })//fetch returns a promise , that we need to mapp to JSON
        .then((res) => res.json())//map it to json
        .then((data) => {//this returns another promise that has the data console.log("data",data)
            emailSuccessOutput.style.display='none'
            if(data.email_error){// 
                emailField.classList.add("is-invalid");//turns the field red
                invalidEmailFeedback.style.display='block'
                invalidEmailFeedback.innerHTML=`<p> ${data.email_error}</p>` //display the Error in the div
                registerBtn.disabled=true;
            }
            else{ // Enable the button once the Error is gone
                registerBtn.removeAttribute("disabled")
            }
        });
    }
})