class Typewriter {
    constructor(element, text, options = {}) {
        this.element = element;
        this.text = text;
        this.wordDelay = options.wordDelay || 150;
        this.fadeSpeed = options.fadeSpeed || 300;
        this.onComplete = options.onComplete;
        this.onInterrupt = options.onInterrupt;
        this.showOptions = options.showOptions || false;
        this.showInput = options.showInput || false;
        this.optionsContainer = options.optionsContainer;
        this.inputContainer = options.inputContainer;
        this.submittedElement = options.submittedElement;
        
        this.isComplete = false;
        this.isInterrupted = false;
        this.timers = [];
        this.words = this.text.split(' ');
        this.currentWordIndex = 0;
        
        this.init();
    }
    
    init() {
        this.element.textContent = '';
        this.addKeyboardListener();
        this.startWordByWordFade();
    }
    
    addKeyboardListener() {
        this.keyHandler = () => {
            if (!this.isComplete && !this.isInterrupted) {
                this.interrupt();
            }
        };
        document.addEventListener('keydown', this.keyHandler);
    }
    
    removeKeyboardListener() {
        if (this.keyHandler) {
            document.removeEventListener('keydown', this.keyHandler);
        }
    }
    
    interrupt() {
        this.isInterrupted = true;
        this.element.textContent = this.text;
        this.element.style.opacity = '1';
        this.hideCaret();
        if (this.showOptions && this.optionsContainer) {
            this.showOptionsField();
        }
        if (this.showInput && this.inputContainer) {
            this.showInputField();
        }
        if (this.onInterrupt) {
            this.onInterrupt();
        }
        this.clearAllTimers();
    }
    
    startWordByWordFade() {
        if (this.isInterrupted) return;
        
        // Create spans for each word
        this.element.innerHTML = '';
        this.wordSpans = [];
        
        this.words.forEach((word, index) => {
            const span = document.createElement('span');
            span.textContent = word;
            span.style.opacity = '0';
            span.style.transition = `opacity ${this.fadeSpeed}ms ease-out`;
            span.style.display = 'inline';
            
            this.wordSpans.push(span);
            this.element.appendChild(span);
            
            // Add space after each word except the last one
            if (index < this.words.length - 1) {
                this.element.appendChild(document.createTextNode(' '));
            }
        });
        
        // Start fading in words one by one
        this.fadeNextWord();
    }
    
    fadeNextWord() {
        if (this.isInterrupted || this.currentWordIndex >= this.words.length) {
            if (this.currentWordIndex >= this.words.length) {
                this.complete();
            }
            return;
        }
        
        const currentSpan = this.wordSpans[this.currentWordIndex];
        currentSpan.style.opacity = '1';
        
        this.currentWordIndex++;
        
        if (this.currentWordIndex < this.words.length) {
            const timer = setTimeout(() => {
                this.fadeNextWord();
            }, this.wordDelay);
            this.timers.push(timer);
        } else {
            // All words are done, complete after a short delay
            const timer = setTimeout(() => {
                this.complete();
            }, this.fadeSpeed);
            this.timers.push(timer);
        }
    }
    
    clearAllTimers() {
        this.timers.forEach(timer => clearTimeout(timer));
        this.timers = [];
    }
    
    complete() {
        const timer = setTimeout(() => {
            this.hideCaret();
            this.isComplete = true;
            if (this.showOptions && this.optionsContainer) {
                setTimeout(() => {
                    this.showOptionsField();
                }, 200);
            }
            if (this.showInput && this.inputContainer) {
                setTimeout(() => {
                    this.showInputField();
                }, 200);
            }
            if (this.onComplete) {
                this.onComplete();
            }
        }, 300);
        this.timers.push(timer);
    }
    
    hideCaret() {
        const caret = this.element.parentElement.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
    }
    
    showOptionsField() {
        if (this.optionsContainer) {
            this.optionsContainer.style.display = 'inline-block';
            
            // Auto-open the dropdown
            const dropdown = this.optionsContainer.querySelector('.custom-dropdown');
            if (dropdown) {
                const dropdownTrigger = dropdown.querySelector('.dropdown-trigger');
                const dropdownOptions = dropdown.querySelector('.dropdown-options');
                
                if (dropdownTrigger && dropdownOptions) {
                    dropdownOptions.style.display = 'block';
                    dropdownTrigger.classList.add('open');
                }
            }
        }
    }
    
    showInputField() {
        if (this.inputContainer) {
            this.inputContainer.style.display = 'inline-block';
            const input = this.inputContainer.querySelector('.inline-input');
            const arrow = this.inputContainer.querySelector('.input-arrow');
            if (input) {
                // Add underline animation after a short delay
                setTimeout(() => {
                    this.inputContainer.classList.add('show-underline');
                }, 100);
                
                // Add input event listener to show/hide arrow
                input.addEventListener('input', () => {
                    if (input.value.trim()) {
                        // Add a small delay before showing the arrow
                        setTimeout(() => {
                            this.inputContainer.classList.add('has-content');
                        }, 300);
                    } else {
                        this.inputContainer.classList.remove('has-content');
                    }
                });
                
                // Add click handler to arrow
                if (arrow) {
                    arrow.addEventListener('click', () => {
                        if (input.value.trim()) {
                            // Trigger the same submit logic as Enter key
                            const enterEvent = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            });
                            input.dispatchEvent(enterEvent);
                        }
                    });
                }
                
                input.focus();
            }
        }
    }
    
    destroy() {
        this.removeKeyboardListener();
        this.clearAllTimers();
    }
}

class SignupForm {
    constructor() {
        this.currentStep = 1;
        this.answers = {};
        this.typewriters = [];
        this.isStarted = false;
        
        this.init();
    }
    
    init() {
        // Add click handler to start onboarding button
        const startBtn = document.getElementById('start-onboarding-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                this.startOnboarding();
            });
        }
    }
    
    startOnboarding() {
        if (this.isStarted) return;
        this.isStarted = true;
        
        const launchScreen = document.getElementById('launch-screen');
        const typewriterForm = document.getElementById('typewriter-form');
        
        // Fade out launch screen
        launchScreen.classList.add('fade-out');
        
        // After fade out, hide launch screen and show typewriter form
        setTimeout(() => {
            launchScreen.style.display = 'none';
            typewriterForm.style.display = 'flex';
            
            // Fade in typewriter form
            setTimeout(() => {
                typewriterForm.classList.add('fade-in');
                
                // Start first question after form is visible
                setTimeout(() => {
                    this.startFirstQuestion();
                }, 200);
            }, 50);
        }, 500);
    }
    
    startFirstQuestion() {
        const question1 = document.getElementById('question1');
        const textElement = question1.querySelector('.typewriter-text');
        const caret = question1.querySelector('.caret');
        const optionsContainer = question1.querySelector('.dropdown-container');
        const dropdown = question1.querySelector('.custom-dropdown');
        const submittedElement = question1.querySelector('.submitted-value');
        
        // Change class to dropdown-specific class
        submittedElement.className = 'submitted-dropdown-value';
        
        // Hide caret
        caret.style.display = 'none';
        
        const typewriter = new Typewriter(textElement, "My company's website or public information on the internet is ", {
            wordDelay: 150,
            fadeSpeed: 300,
            showOptions: true,
            optionsContainer: optionsContainer,
            submittedElement: submittedElement,
            onComplete: () => {
                this.setupDropdownHandler(dropdown, submittedElement, (value) => {
                    this.answers.company = value;
                    if (value.toLowerCase().trim() === 'available') {
                        this.startDomainQuestion();
                    } else {
                        this.startLegalNameQuestion();
                    }
                });
            },
            onInterrupt: () => {
                this.setupDropdownHandler(dropdown, submittedElement, (value) => {
                    this.answers.company = value;
                    if (value.toLowerCase().trim() === 'available') {
                        this.startDomainQuestion();
                    } else {
                        this.startLegalNameQuestion();
                    }
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    
    startDomainQuestion() {
        const question1 = document.getElementById('question1');
        const question2 = document.getElementById('question2');
        
        const submittedElementQ1 = question1.querySelector('.submitted-dropdown-value');
        submittedElementQ1.insertAdjacentElement('afterend', question2);
        question2.style.display = 'inline';
        
        const textElement = question2.querySelector('.typewriter-text');
        const inputContainer = question2.querySelector('.input-container');
        const inputElement = question2.querySelector('.inline-input');
        const submittedElement = question2.querySelector('.submitted-value');
        
        const caret = question2.querySelector('.caret');
        if (caret) caret.style.display = 'none';
        
        const typewriter = new Typewriter(textElement, " our website URL is", {
            wordDelay: 120,
            fadeSpeed: 300,
            showInput: true,
            inputContainer: inputContainer,
            submittedElement: submittedElement,
            onComplete: () => {
                this.setupInputHandler(inputElement, submittedElement, (value) => {
                    this.answers.domain = value;
                    this.startDomainChoiceStep2(); // 🔥 call this instead of final step
                });
            },
            onInterrupt: () => {
                this.setupInputHandler(inputElement, submittedElement, (value) => {
                    this.answers.domain = value;
                    this.startDomainChoiceStep2();
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    
    

    
    startLegalNameQuestion() {
        const question1 = document.getElementById('question1');
        const question3 = document.getElementById('question3');
        
        // Insert the third question inline after the first question's submitted value
        const submittedElementQ1 = question1.querySelector('.submitted-dropdown-value');
        submittedElementQ1.insertAdjacentElement('afterend', question3);
        question3.style.display = 'inline';
        
        const textElement = question3.querySelector('.typewriter-text');
        const inputContainer = question3.querySelector('.input-container');
        const inputElement = question3.querySelector('.inline-input');
        const submittedElement = question3.querySelector('.submitted-value');
        
        // Hide the caret for the third question
        const caret = question3.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
        
        const typewriter = new Typewriter(textElement, " and our legal name is", {
            wordDelay: 120,
            fadeSpeed: 300,
            showInput: true,
            inputContainer: inputContainer,
            submittedElement: submittedElement,
            onComplete: () => {
                this.setupInputHandler(inputElement, submittedElement, (value) => {
                    this.answers.legalName = value;
                    this.startDomainChoiceStep();
                });
            },
            onInterrupt: () => {
                this.setupInputHandler(inputElement, submittedElement, (value) => {
                    this.answers.legalName = value;
                    this.startDomainChoiceStep();
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    
    startDomainChoiceStep() {
        const question3 = document.getElementById('question3');
        const question4 = document.getElementById('question4');
        
        // Insert the fourth question inline after the third question's input
        const submittedElement = question3.querySelector('.submitted-value');
        submittedElement.insertAdjacentElement('afterend', question4);
        question4.style.display = 'inline';
        
        const textElement = question4.querySelector('.typewriter-text');
        const inputContainer = question4.querySelector('.input-container');
        const inputElement = question4.querySelector('.inline-input');
        const submittedElementQuestion4 = question4.querySelector('.submitted-value');
        
        // Hide the caret for the fourth question
        const caret = question4.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
        
        const typewriter = new Typewriter(textElement, " The domain I choose for registering in the Gaia-X ecosystem is", {
            wordDelay: 100,
            fadeSpeed: 300,
            showInput: true,
            inputContainer: inputContainer,
            submittedElement: submittedElementQuestion4,
            onComplete: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion4, (value) => {
                    this.answers.domainChoice = value;
                    this.startCompanyDescriptionStep();
                });
            },
            onInterrupt: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion4, (value) => {
                    this.answers.domainChoice = value;
                    this.startCompanyDescriptionStep();
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    startDomainChoiceStep2() {
        const question3 = document.getElementById('question2');
        const question4 = document.getElementById('question4');
        
        // Insert the fourth question inline after the third question's input
        const submittedElement = question3.querySelector('.submitted-value');
        submittedElement.insertAdjacentElement('afterend', question4);
        question4.style.display = 'inline';
        
        const textElement = question4.querySelector('.typewriter-text');
        const inputContainer = question4.querySelector('.input-container');
        const inputElement = question4.querySelector('.inline-input');
        const submittedElementQuestion4 = question4.querySelector('.submitted-value');
        
        // Hide the caret for the fourth question
        const caret = question4.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
        
        const typewriter = new Typewriter(textElement, " The domain I choose for registering in the Gaia-X ecosystem is", {
            wordDelay: 100,
            fadeSpeed: 300,
            showInput: true,
            inputContainer: inputContainer,
            submittedElement: submittedElementQuestion4,
            onComplete: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion4, (value) => {
                    this.answers.domainChoice = value;
                    this.startFinalStep();
                });
            },
            onInterrupt: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion4, (value) => {
                    this.answers.domainChoice = value;
                    this.startFinalStep();
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    
    startCompanyDescriptionStep() {
        const question4 = document.getElementById('question4');
        const question5 = document.getElementById('question5');
        
        // Insert the fifth question inline after the fourth question's input
        const submittedElement = question4.querySelector('.submitted-value');
        submittedElement.insertAdjacentElement('afterend', question5);
        question5.style.display = 'inline';
        
        const textElement = question5.querySelector('.typewriter-text');
        const inputContainer = question5.querySelector('.input-container');
        const inputElement = question5.querySelector('.inline-input');
        const submittedElementQuestion5 = question5.querySelector('.submitted-value');
        
        // Hide the caret for the fifth question
        const caret = question5.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
        
        const typewriter = new Typewriter(textElement, " My company, in short, is engaged in", {
            wordDelay: 120,
            fadeSpeed: 300,
            showInput: true,
            inputContainer: inputContainer,
            submittedElement: submittedElementQuestion5,
            onComplete: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion5, (value) => {
                    this.answers.companyDescription = value;
                    this.startFinalStep();
                });
            },
            onInterrupt: () => {
                this.setupInputHandler(inputElement, submittedElementQuestion5, (value) => {
                    this.answers.companyDescription = value;
                    this.startFinalStep();
                });
            }
        });
        
        this.typewriters.push(typewriter);
    }
    
    startFinalStep() {
        // Find the last submitted element to insert after
        let lastSubmittedElement;
        if (this.answers.companyDescription) {
            lastSubmittedElement = document.getElementById('question5').querySelector('.submitted-value');
        } else if (this.answers.domain) {
            lastSubmittedElement = document.getElementById('question4').querySelector('.submitted-value');
        }
        
        const question6 = document.getElementById('question6');
        
        // Insert the final step inline after the last submitted value
        if (lastSubmittedElement) {
            lastSubmittedElement.insertAdjacentElement('afterend', question6);
            question6.style.display = 'inline';
        }
        
        const textElement = question6.querySelector('.typewriter-text');
        const buttonElement = question6.querySelector('.create-account-btn');
        
        // Hide the caret for the final question
        const caret = question6.querySelector('.caret');
        if (caret) {
            caret.style.display = 'none';
        }
        
        const typewriter = new Typewriter(textElement, " Great, you are all set 🚀", {
            wordDelay: 150,
            fadeSpeed: 300,
            showInput: false,
            onComplete: () => {
                
                // Add rocket SVG after text completion
                // setTimeout(() => {
                //   const rocketSvg = document.createElement('span');
                //   rocketSvg.innerHTML = `
                // <svg width="40" height="40" viewBox="0 0 24 24"
                //      xmlns="http://www.w3.org/2000/svg"
                //      style="display:inline-block; margin-left:-5px; vertical-align:-0.8em">
                //   <defs>
                //     <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
                //       <stop offset="0" stop-color="#60A5FA"/>
                //       <stop offset="1" stop-color="#2563EB"/>
                //     </linearGradient>
                //     <linearGradient id="f" x1="0" y1="0" x2="0" y2="1">
                //       <stop offset="0" stop-color="#FFE08A"/>
                //       <stop offset="1" stop-color="#FF6B6B"/>
                //     </linearGradient>
                //   </defs>
                
                //   <!-- گروه شناور -->
                //   <g>
                //     <animateTransform attributeName="transform" type="translate"
                //       values="0 0; 0 -1; 0 0" dur="1.8s" repeatCount="indefinite"/>
                //     <!-- کمی چرخش برای حس پرتاب -->
                //     <g transform="translate(12 12) rotate(30) translate(-12 -12)">
                //       <!-- بدنه -->
                //       <rect x="9" y="6" width="6" height="10" rx="3"
                //             fill="#fff" stroke="url(#b)" stroke-width="1.5"/>
                //       <!-- نوک -->
                //       <path d="M12 3 L14.6 6 H9.4 Z" fill="url(#b)"/>
                //       <!-- موتور/نازل -->
                //       <path d="M9.4 16 H14.6 L13.6 18 H10.4 Z" fill="url(#b)"/>
                //       <!-- بالچه‌ها -->
                //       <path d="M9.4 12 L7.6 14 H9.4 Z" fill="url(#b)"/>
                //       <path d="M14.6 12 L16.4 14 H14.6 Z" fill="url(#b)"/>
                //       <!-- پنجره -->
                //       <circle cx="12" cy="10" r="1.7" fill="#E8F1FF"
                //               stroke="url(#b)" stroke-width="1"/>
                //       <circle cx="12.6" cy="9.6" r="0.6" fill="#fff" opacity=".9"/>
                
                //       <!-- شعله -->
                //       <g transform="translate(12 18)">
                //         <path d="M0 0 C 1.9 1.6, 1.9 4.2, 0 6 C -1.9 4.2, -1.9 1.6, 0 0 Z"
                //               fill="url(#f)" opacity=".95">
                //           <animateTransform attributeName="transform" type="scale"
                //             values="1 1; 1 0.82; 1 1" dur="0.35s" repeatCount="indefinite"/>
                //           <animate attributeName="opacity"
                //             values="0.95;0.8;0.95" dur="0.35s" repeatCount="indefinite"/>
                //         </path>
                //       </g>
                //     </g>
                //   </g>
                // </svg>`;
                //   textElement.appendChild(rocketSvg);
                // }, 500);


                
                
                setTimeout(() => {
                    buttonElement.style.display = 'flex';
                    buttonElement.style.opacity = '0';
                    setTimeout(() => {
                        buttonElement.style.transition = 'opacity 600ms ease-out';
                        buttonElement.style.opacity = '1';
                    }, 50);
                }, 200);
            }
        });
        
        this.typewriters.push(typewriter);
        
        
    }
    
    setupDropdownHandler(dropdown, submittedElement, onSubmit) {
        const questionElement = dropdown.closest('[id^="question"]');
        const questionId = questionElement ? questionElement.id : null;
        const dropdownTrigger = dropdown.querySelector('.dropdown-trigger');
        const dropdownOptions = dropdown.querySelector('.dropdown-options');
        const dropdownText = dropdown.querySelector('.dropdown-text');
        const dropdownArrow = dropdown.querySelector('.dropdown-arrow');
        
        // Add click handler to dropdown trigger
        dropdownTrigger.addEventListener('click', () => {
            const isOpen = dropdownOptions.style.display === 'block';
            
            if (isOpen) {
                // Close dropdown
                dropdownOptions.style.display = 'none';
                dropdownTrigger.classList.remove('open');
            } else {
                // Open dropdown
                dropdownOptions.style.display = 'block';
                dropdownTrigger.classList.add('open');
            }
        });
        
        // Add click handlers to options
        const options = dropdown.querySelectorAll('.dropdown-option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                const value = option.getAttribute('data-value');
                
                // Remove selected class from all options
                options.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected class to clicked option
                option.classList.add('selected');
                
                // Clear all subsequent questions when submitting edit
                if (questionId) {
                    this.clearSubsequentQuestionsFrom(questionId);
                }
                
                // Close dropdown
                dropdownOptions.style.display = 'none';
                dropdownTrigger.classList.remove('open');
                
                // Hide dropdown
                dropdown.style.display = 'none';
                
                // Show submitted value
                submittedElement.textContent = value;
                submittedElement.style.display = 'inline';
                
                // Make submitted value clickable for editing
                submittedElement.style.cursor = 'pointer';
                submittedElement.title = 'Click to change selection';
                
                // Add click handler for editing (remove previous listeners first)
                submittedElement.onclick = () => {
                    // Hide submitted value
                    submittedElement.style.display = 'none';
                    
                    // Show dropdown again
                    dropdown.style.display = 'inline-block';
                    
                    // Reset dropdown text
                    dropdownText.textContent = 'Select option...';
                    
                    // Auto-open dropdown immediately
                    dropdownTrigger.classList.add('open');
                    dropdownOptions.style.display = 'block';
                    
                    // Add click outside listener
                    setTimeout(() => {
                        document.addEventListener('click', handleClickOutside);
                    }, 0);
                };
                
                // Hide caret after selection
                const caret = questionElement.querySelector('.caret');
                if (caret) {
                    caret.style.display = 'none';
                }
                
                // Call the callback
                setTimeout(() => {
                    onSubmit(value);
                }, 500);
            });
        });
        
        // Add click outside listener to close dropdown
        const handleClickOutside = (event) => {
            if (!dropdown.contains(event.target) && !submittedElement.contains(event.target)) {
                // Close dropdown
                dropdownOptions.style.display = 'none';
                dropdownTrigger.classList.remove('open');
                
                // If there's a submitted value, restore it; otherwise hide dropdown
                if (submittedElement.textContent.trim()) {
                    submittedElement.style.display = 'inline';
                    dropdown.style.display = 'none';
                } else {
                    // No selection made, keep dropdown visible but closed
                    dropdown.style.display = 'inline-block';
                }
                
                // Remove the click outside listener
                document.removeEventListener('click', handleClickOutside);
            }
        };
    }
    
    setupInputHandler(inputElement, submittedElement, onSubmit) {
        // Store the original value for editing
        let originalValue = '';
        let questionElement = inputElement.closest('[id^="question"]');
        let questionId = questionElement ? questionElement.id : null;
        
        const handleSubmit = () => {
            const value = inputElement.value.trim();
            if (value) {
                // Only clear subsequent questions if the value actually changed
                const valueChanged = originalValue !== value;
                
                if (valueChanged && questionId) {
                    this.clearSubsequentQuestionsFrom(questionId);
                }
                
                originalValue = value;
                
                // Hide input
                const container = inputElement.parentElement;
                container.style.display = 'none';
                
                // Show submitted value
                submittedElement.textContent = value;
                submittedElement.style.display = 'inline';
                
                // Only call the callback if value changed
                if (valueChanged) {
                    setTimeout(() => {
                        onSubmit(value);
                    }, 500);
                }
            }
        };
        
        // Add click handler to submitted value for editing
        submittedElement.addEventListener('click', () => {
            // Hide submitted value
            submittedElement.style.display = 'none';
            
            // Show input container again
            const container = inputElement.parentElement;
            container.style.display = 'inline-block';
            
            // Set the original value back to input
            inputElement.value = originalValue;
            
            // Add underline animation
            setTimeout(() => {
                container.classList.add('show-underline');
                if (inputElement.value.trim()) {
                    container.classList.add('has-content');
                }
            }, 100);
            
            // Focus on input
            inputElement.focus();
            
            // Add click outside listener
            setTimeout(() => {
                document.addEventListener('click', handleClickOutside);
            }, 0);
        });
        
        // Make submitted value look clickable
        submittedElement.style.cursor = 'pointer';
        submittedElement.title = 'Click to edit';
        
        inputElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                handleSubmit();
            }
        });
        
        // Also handle arrow click
        const arrow = inputElement.parentElement.querySelector('.input-arrow');
        if (arrow) {
            arrow.addEventListener('click', () => {
                if (inputElement.value.trim()) {
                    handleSubmit();
                }
            });
        }
        
        // Add click outside listener to close input editing
        const handleClickOutside = (event) => {
            const inputContainer = inputElement.parentElement;
            if (!inputContainer.contains(event.target) && !submittedElement.contains(event.target)) {
                // Close input and restore original value
                inputContainer.style.display = 'none';
                submittedElement.style.display = 'inline';
                
                // Reset input value to original
                inputElement.value = originalValue;
                
                // Remove the click outside listener
                document.removeEventListener('click', handleClickOutside);
            }
        };
    }
    
    clearSubsequentQuestionsFrom(fromQuestionId) {
        // Get all questions that come after the specified question
        const allQuestions = ['question1', 'question2', 'question3', 'question4', 'question5', 'question6'];
        const fromIndex = allQuestions.indexOf(fromQuestionId);
        const questionsToReset = allQuestions.slice(fromIndex + 1);
        
        questionsToReset.forEach(questionId => {
            const questionElement = document.getElementById(questionId);
            if (questionElement) {
                questionElement.style.display = 'none';
                
                // Reset typewriter text
                const textElement = questionElement.querySelector('.typewriter-text');
                if (textElement) {
                    textElement.textContent = '';
                }
                
                // Reset and hide input containers
                const inputContainer = questionElement.querySelector('.input-container');
                if (inputContainer) {
                    inputContainer.style.display = 'none';
                    const input = inputContainer.querySelector('.inline-input');
                    if (input) {
                        input.value = '';
                        inputContainer.classList.remove('show-underline', 'has-content');
                    }
                }
                
                // Reset and hide dropdown containers
                const dropdownContainer = questionElement.querySelector('.dropdown-container');
                if (dropdownContainer) {
                    dropdownContainer.style.display = 'none';
                    const dropdown = dropdownContainer.querySelector('.dropdown-select');
                    if (dropdown) {
                        dropdown.value = '';
                    }
                }
                
                // Reset and hide submitted values
                const submittedElement = questionElement.querySelector('.submitted-value');
                if (submittedElement) {
                    submittedElement.style.display = 'none';
                    submittedElement.textContent = '';
                }
                
                // Reset caret
                const caret = questionElement.querySelector('.caret');
                if (caret) {
                    caret.style.display = 'inline-block';
                }
                
                // Reset button
                const button = questionElement.querySelector('.create-account-btn');
                if (button) {
                    button.style.display = 'none';
                }
            }
        });
        
        // Destroy typewriters for reset questions
        const typewritersToKeep = fromIndex + 1;
        if (this.typewriters.length > typewritersToKeep) {
            for (let i = typewritersToKeep; i < this.typewriters.length; i++) {
                this.typewriters[i].destroy();
            }
            this.typewriters = this.typewriters.slice(0, typewritersToKeep);
        }
        
        // Reset answers for subsequent questions
        const answersToKeep = {};
        if (fromIndex >= 0) answersToKeep.company = this.answers.company;
        if (fromIndex >= 1) answersToKeep.domain = this.answers.domain;
        if (fromIndex >= 2) answersToKeep.legalName = this.answers.legalName;
        if (fromIndex >= 3) answersToKeep.domainChoice = this.answers.domainChoice;
        if (fromIndex >= 4) answersToKeep.companyDescription = this.answers.companyDescription;
        
        this.answers = answersToKeep;
    }
    

    
    destroy() {
        this.typewriters.forEach(typewriter => typewriter.destroy());
    }
}

// Initialize the form when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SignupForm();
});