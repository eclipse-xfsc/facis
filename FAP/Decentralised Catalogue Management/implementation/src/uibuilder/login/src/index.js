const { createApp } = Vue;

createApp({
    data() {
        return {
            route: 'login',
            email: '',
            password: '',
            confirmPassword: '',
            fullName: '',
            role: '',
            showPassword: false,
            showConfirmPassword: false,
            rememberMe: false,
            acceptTerms: false,
            emailError: '',
            passwordError: '',
            newPasswordError:"",
            confirmPasswordError: '',
            showForgotPasswordModal: false,
            resetEmail: '',
            showVerificationCode: false,
            verificationDigits: ['', '', '', '', '', ''],
            verificationInputs: [],
            timerSeconds: 10,
            timerInterval: null,
            showVerificationLoading: false,
            showVerificationSuccess: false,
            showSetNewPassword: false,
            newPassword: '',
            confirmNewPassword: '',
            showNewPassword: false,
            showConfirmNewPassword: false,
            invalidCredentialsError : "",
            invalidEmail: "",
            expireCode: "",
            invalidCode: "",
        }
    },
    computed: {
        timerText() {
            const minutes = Math.floor(this.timerSeconds / 60);
            const seconds = this.timerSeconds % 60;
            return `${minutes}:${seconds.toString().padStart(2, '0')} remaining`;
        }
    },
    methods: {
        
        getCookie: function (name) {
          let value = "; " + document.cookie;
          let parts = value.split("; " + name + "=");
          if (parts.length == 2) return parts.pop().split(";").shift();
        },
    
        login() {
            this.route = "login";
        },

        togglePassword() {
            this.showPassword = !this.showPassword;
        },

        toggleConfirmPassword() {
            this.showConfirmPassword = !this.showConfirmPassword;
        },

        validateEmail() {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!this.email) {
                this.emailError = 'Email is required';
                return false;
            } else if (!emailPattern.test(this.email)) {
                this.emailError = 'Please enter a valid email address with @';
                return false;
            } else {
                this.emailError = '';
                return true;
            }
        },

        validatePassword() {
            if (!this.password) {
                this.passwordError = 'Password is required';
                return false;
            } else if (this.password.length < 6) {
                this.passwordError = 'Password must be at least 6 characters';
                return false;
            } else {
                this.passwordError = '';
                return true;
            }
        },

        validateConfirmPassword() {
            if (!this.confirmPassword) {
                this.confirmPasswordError = 'Please confirm your password';
                return false;
            } else if (this.password !== this.confirmPassword) {
                this.confirmPasswordError = 'Passwords do not match';
                return false;
            } else {
                this.confirmPasswordError = '';
                return true;
            }
        },

        resetPassword() {
            this.startTimer();
            uibuilder.send({
                auth: {
                    type : "resetPassword",
                    email: this.resetEmail
                }
            })
            
        },
        

        startTimer() {
            this.timerSeconds = 120;
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }
            this.timerInterval = setInterval(() => {
                if (this.timerSeconds > 0) {
                    this.timerSeconds--;
                } else {
                    clearInterval(this.timerInterval);
                    this.expireCode = "Your code has been expired.";
                }
            }, 1000);
        },

        handleDigitInput(index, event) {
            let value = event.target.value;

            if (!/^\d*$/.test(value)) {
                event.target.value = '';
                this.verificationDigits[index] = '';
                return;
            }

            if (value && index < 5) {
                this.verificationInputs[index + 1].focus();
            } else if (value && index === 5) {
                const allFilled = this.verificationDigits.every(digit => digit !== '');
                if (allFilled) {

                    const code = this.verificationDigits.join('');
                    uibuilder.send({
                        auth: {
                            type: "sendResetCode",
                            email: this.resetEmail,
                            code: code
                        }
                    });
                    this.showVerificationSuccess = true;

                }
            }
        },
        
        handleKeyDown(index, event) {
            if (event.key === 'Backspace' && !this.verificationDigits[index] && index > 0) {
                this.verificationInputs[index - 1].focus();
            }
        },
        


        resendCode() {
            this.verificationDigits = ['', '', '', '', '', ''];
            this.verificationInputs[0].focus();
            this.startTimer();
            this.expireCode = "",
            
            uibuilder.send({
                auth:{
                    email: this.resetEmail,
                    type: "resendResetPassword",
                }
            })
        },
        

        closeVerificationModal() {
            this.showVerificationCode = false;
            this.showForgotPasswordModal = false;
            this.verificationDigits = ['', '', '', '', '', ''];
            this.expireCode = "";
            this.invalidCode = "";
            this.invalidEmail = "";
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }
            uibuilder.send({
                auth:{
                    email: this.resetEmail,
                    type: "cancelResetPassword"
                    
                }
            });
            
        },
        

        closeSetNewPasswordModal() {
            this.showSetNewPassword = false;
            this.newPassword = '';
            this.confirmNewPassword = '';
            this.resetEmail = '';
        },

        submitNewPassword() {
            if (!this.newPassword) {
                this.newPasswordError = 'Please enter a new password'
            }
            else if (this.newPassword !== this.confirmNewPassword) {
                this.newPasswordError = 'Passwords do not match'
            }else{
                uibuilder.send({
                    auth : {
                        type: "setNewPassword",
                        email: this.resetEmail,
                        password: this.newPassword
                    }
                })
                this.closeSetNewPasswordModal();
            }
            

        },

        toggleNewPassword() {
            this.showNewPassword = !this.showNewPassword;
        },

        toggleConfirmNewPassword() {
            this.showConfirmNewPassword = !this.showConfirmNewPassword;
        },

        signinButton(){
            const isEmailValid = this.validateEmail();
            const isPasswordValid = this.validatePassword();

            if (!isEmailValid || !isPasswordValid) {
                return;
            }

            const clientId = uibuilder.get("clientId")
            uibuilder.send({
                auth: {
                   // clientId: clientId,
                    email: this.email,
                    password: this.password,
                   // rememberMe: this.rememberMe,
                    type: "login"

                }
            })
        },

    },

    mounted() {
        uibuilder.start();
        if (this.getCookie("userToken")) {
          uibuilder.send({
            auth: {
              userToken: this.getCookie("userToken"),
              clientId: this.getCookie("uibuilder-client-id"),
            },
          });
        } else {
          uibuilder.send({
            auth: {
              userToken: null,
              clientId: this.getCookie("uibuilder-client-id"),
            },
          });
        }
        
        var vueApp = this
        uibuilder.onChange('msg',function(msg) {

            if(msg.payload.action === "verifyEmail" && msg.payload.status === "expiredCode"){
                vueApp.expireCode = msg.payload.message
                vueApp.signupVerificationDigits = ['', '', '', '', '', ''];
                setTimeout(() => {
                   if (vueApp.signupVerificationInputs[0]) {
                        vueApp.signupVerificationInputs[0].focus();
                    }
                }, 100);
            }
           // 
            if(msg.payload.action === "verifyEmail" && msg.payload.status === "invalidCode"){
                vueApp.invalidCode = msg.payload.message
                vueApp.signupVerificationDigits = ['', '', '', '', '', ''];
                setTimeout(() => {
                    if (vueApp.signupVerificationInputs[0]) {
                        vueApp.signupVerificationInputs[0].focus();
                    }
                }, 100);
            }
            
            
            if(msg.payload.action === "login" && msg.payload.status === "redirect"){
                window.location.replace(
                    '/atoosa-dcm/Dashboard/'
                )
            }
            
            if(msg.payload.action === "login" && msg.payload.status === "invalidCredentials"){
                if (msg.payload?.message) {
                  vueApp.invalidCredentialsError = msg.payload.message
                }
            }
            
            if(msg.payload.action === "login" && msg.payload.status === "success"){
                
                document.cookie = "userToken=" + msg.auth.userToken + ";path=/;max-age=604800;Secure;SameSite=Strict"
                window.location.replace(
                    '/atoosa-dcm/Dashboard/'
                )
            }
            
            if(msg.payload.action === "resetPassword" && msg.payload.status === "invalidEmail"){
                vueApp.invalidEmail = msg.payload.message
            }
            
            if(msg.payload.action === "resetPassword" && msg.payload.status === "validEmail"){
                vueApp.showVerificationCode = true;
                vueApp.invalidEmail = ""
                setTimeout(() => {
                    if (vueApp.verificationInputs[0]) {
                        vueApp.verificationInputs[0].focus();
                    }
                }, 100);
            }
            
            if(msg.payload.action === "resetPassword" && msg.payload.status === "expired"){
                vueApp.invalidCode = "";
                vueApp.expireCode = msg.payload.message
                vueApp.verificationDigits = ['', '', '', '', '', ''];
                vueApp.startTimer();
            }

            if(msg.payload.action === "resetPassword" && msg.payload.status === "invalidCode"){
                vueApp.invalidCode = msg.payload.message
                vueApp.verificationDigits = ['', '', '', '', '', ''];
                vueApp.verificationInputs[0].focus();
            }
            
            if(msg.payload.action === "resetPassword" && msg.payload.status === "validCode"){
                vueApp.showVerificationSuccess = false;
                vueApp.showVerificationCode = false;
                vueApp.showVerificationLoading = false;
                vueApp.showForgotPasswordModal = false;
                vueApp.verificationDigits = ['', '', '', '', '', ''];
                vueApp.showSetNewPassword = true;
                vueApp.invalidCode = "";
            }

            if(msg.payload.action === "setNewPassword" && msg.payload.status === "success"){
                vueApp.showSetNewPassword = false;
                vueApp.newPasswordError = "";
            }
            
        })
        
    }
}).mount('#app');