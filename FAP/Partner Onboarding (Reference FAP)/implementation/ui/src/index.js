// @ts-nocheck
'use strict'

const { createApp } = Vue
const app = createApp({

    data() {
        return {
          startText:'',
          currentStep: 'pg1', // 'onboarding' or 'form'
          isAnimating: false,
          isFadingOut: false,
          isFadingIn: false,
          isExpanding: false,
          isExpanded: false,
          certificatePopUp: "none",
          hasdomain: null,
          termsAccepted: false,
          verifyError: false,
          
          // Form states
          showTeamA: false,
          showTeamB: false,
          showTeamC: false,
          showTeamD: false,
          showBusinessDetailsA: false,
          showBusinessDetailsB: false,
          showBusinessDetailsC: false,
          showStateA: true,
          showStateB: false,
          showCompanyType: true,
          showCompletion: false,
          showCompletionB: false,
          showCompletionC: false,
          showCompletionD: false,
          showLeftWhite: true, 
          businessComplete: false,
          teamComplete: false,
          companyComplete: true,
          stateComplete: false,
          editCompanyDetails: false,
          currentJson: null,
          allFilledData: false,
          notAvailable: null,
          selectedClearingHouse: "none",
          selectedCompliance: "none",
          versionCompliance: "V2",
          gaiax: false,
          pfalzkom: false,
          deltaDao: false,
          aruba: false,
          ovhCloud: false,
          proximus: false,
          tsystem: false,
          aireNetwork: false,
          neustaAerospace: false,
          cispe: false,
          arsys: false,

          showJson: false,
          
          directors: [
            { firstName: '', lastName: '' } 
          ],
          officers: [
            { firstName: '', lastName: '' } 
          ],
          
          companyData: {},
          participantVC: {},
          termsAndConditionsVC: {},
          legalVC: {},
          launch: {},
          animationData: [],
          answers: {
                question1: '',
                question2: '',
                question3: '',
                question4: '',
                question5: ''
            },
          selectedCertificate: 'extended-validation',
          selectedDID: 'extended-validation',
           uploadStatuses: {
                bundle: 'none',       // none | uploading | success | failed
                certificate: 'none',
                privateKey: 'none'
            },
            uploadedFiles: {
              bundle: null,
              certificate: null,
              privateKey: null
            },
            chainUrl: null,
            didUrl: null,
            didFileName: "",
            chainFileName: "",
            DIDButtonState: 'default', 
            ChainButtonState: 'default',
            didURL: "",
            chainURL:"",
            onboardingPackage:{},
            formData: {
                lrnVCid: "",
                lrnSid: "",
                tcVCid: "",
                tcSid: "",
                pVCid: "",
                pSid: ""
            },
            loadVerify: false,
            loadVC: false,
            loadVCJson: false,
            loadClearing: false,
            isOpen: false,
            userInput: '',
            messages: [],
            messageId: 1,
            ws: null,
            isConnected: false,
            category:  {
                      "chatbot": {
                        "title": "Gaia-X Onboarding Assistant",
                    
                        "suggestions": {
                          "suggestion1": "What is the first step in the Gaia-X onboarding process?",
                          "suggestion2": "How do I upload my certificates (.crt, .bundle, .key)?",
                          "suggestion3": "What is a DID and why do I need one?",
                          "suggestion4": "How can I create or verify my Verifiable Credentials (VCs)?",
                          "suggestion5": "Which Gaia-X version should I choose — v22.04 or Danube (v23.12)?"
                        },
                        "input": {
                          "placeholder": "Ask me anything..."
                        }
                      },
                    
                      "onboardingScreen": {
                        "ctaButton": "START ONBOARDING"
                      },
                    
                      "typewriterForm": {
                        "dropdown": {
                          "placeholder": "Select option...",
                          "options": {
                            "available": "Available",
                            "notAvailable": "Not Available"
                          }
                        },
                        "finalStep": {
                          "buttonLabel": "Confirm & Next"
                        }
                      },
                    
                      "modalFirst": {
                        "disclaimer": "This wizard uses the OpenAI API only to retrieve information from the internet. Your inputs will not be transmitted, stored, or processed by OpenAI. All data remains fully owned, managed, and stored within the FACIS proprietary LLM, and will not be shared with any third parties. The OpenAI API is used exclusively as a tool for accessing internet resources, without transferring your data to OpenAI.",
                        "buttons": {
                          "cancel": "Cancel",
                          "confirm": "Confirm"
                        }
                      },
                      "verificationForm": {
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        },
                        "title": "Verify Your Company Details",
                        "subtitle": "We found the following information linked to your domain. Please review and confirm.",
                        "viewJsonButton": "View Json",
                        "actions": {
                          "editDetails": {
                            "title": "Edit Details",
                            "subtitle": "Needs update"
                          },
                          "confirmCompany": {
                            "title": "This is my company",
                            "subtitle": "Details are correct"
                          }
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "confirmAndProgress": "Confirm & Progressed"
                        }
                      },
                      "companyCard": {
                        "sections": {
                          "companyDetails": "Company Details",
                          "legalRegistration": "Legal Registration",
                          "legalIdentifiers": "Legal Identifiers",
                          "management": "Management",
                          "headquartersAddress": "Headquarters Address",
                          "contact": "Contact",
                          "sourcesAndVerification": "Sources & Verification"
                        },
                        "labels": {
                          "onboardingDomain": "Onboarding Domain",
                          "legalCompanyName": "Legal Company Name",
                          "websiteDomain": "Website / Domain",
                          "legalForm": "Legal Form",
                          "registrationNumber": "Registration Number",
                          "registeringAuthority": "Registering Authority / Court",
                          "previousRegistrationNumber": "Previous Registration Number",
                          "previousRegisteringAuthority": "Previous Registering Authority / Court",
                          "registrationNotes": "Notes",
                          "euVatId": "EU VAT ID",
                          "taxId": "Tax ID",
                          "euid": "EUID",
                          "eoriNumber": "EORI Number",
                          "leiCode": "LEI Code",
                          "boardChair": "Board Chair",
                          "viceChair": "Vice Chair",
                          "managingDirectors": "Managing Directors",
                          "boardMembers": "Board Members",
                          "streetAddress": "Street Address",
                          "postalCode": "Postal Code",
                          "city": "City",
                          "stateOrRegion": "State / Region",
                          "stateOrRegionCode": "State / Region Code",
                          "country": "Country",
                          "countryCode": "Country Code",
                          "phone": "Phone",
                          "email": "Email",
                          "website": "Website",
                          "sourceLinks": "Source Links",
                          "lastVerifiedDate": "Last Verified Date"
                        }
                      },
                    
                      "editSection": {
                        "formLabels": {
                          "onboardingDomain": "Onboarding Domain",
                          "domainAddress": "Domain Address",
                          "legalCompanyName": "Legal Company Name",
                          "legalAddressIso": "Legal address (ISO 3166-2)",
                          "headquarterAddressIso": "Headquarter address (ISO 3166-2)",
                          "onlyOneRequired": "Only One Required",
                          "euVatId": "EU VAT ID",
                          "taxId": "Tax ID",
                          "euid": "EUID"
                        },
                        "placeholders": {
                          "domainExample": "example.com",
                          "companyNameExample": "Company Name Inc.",
                          "legalAddressPlaceholder": "Enter legal address...",
                          "headquarterAddressPlaceholder": "Enter headquarter address..."
                        }
                      },
                      "stepsNavigation": {
                        "steps": {
                          "step1": "COMPANY SETUP",
                          "step2": "CERTIFICATE",
                          "step3": "DID SETUP",
                          "step4": "CREDENTIALS (VCs)",
                          "step5": "COMPLETION"
                        },
                        "subSteps": {
                          "certificate": {
                            "substep1": "Certificate Type",
                            "substep2": "Upload Certificate"
                          },
                          "didSetup": {
                            "substep1": "DID Options",
                            "substep2": "Download DID & Chain",
                            "substep3": "Verify Publishing"
                          },
                          "credentialsVc": {
                            "substep1": "Issuer & Verification Method",
                            "substep2": "Gaia-X Version",
                            "substep3": "Prepare Credentials",
                            "substep4": "Review & Sign"
                          },
                          "completion": []
                        }
                      },
                      "whichTypeOfCertificateDoYouHave": {
                        "title": "Which type of certificate do you have?",
                        "subtitle": "We detected a Domain Validation (DV) certificate associated with your website. Please confirm or choose the option that best applies to you in order to continue.",
                        "options": {
                          "noAccess": {
                            "title": "Without Access",
                            "description": "I don't have access to my certificate files"
                          },
                          "extendedValidation": {
                            "title": "EV",
                            "description": "I have an Extended Validation (EV) certificate"
                          },
                          "dvOrOv": {
                            "title": "DV or OV",
                            "description": "I only have a DV or OV certificate"
                          }
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        },
                        "certificateModal": {
                          "title": "Confirm your certificate type",
                          "description": "The OV/DV certificate is issued solely for use in Staging/Test Environments. This certificate is not valid in Production environments and is only intended for testing, verification, and simulation of processes before deployment to the live environment.",
                          "buttons": {
                            "back": "Back",
                            "confirm": "Confirm"
                          }
                        }
                      },
                    
                      "uploadYourCertificateFiles": {
                        "title": "Upload your certificate files",
                        "subtitle": "To continue, please upload your RSA certificate file. You'll need three parts: the main certificate, the bundle, and your private key",
                        "uploadCards": {
                          "bundle": {
                            "label": "Certificate bundle",
                            "subLabel": "intermediate certificates"
                          },
                          "certificate": {
                            "label": "Certificate file",
                            "subLabel": "your domain certificate"
                          },
                          "privateKey": {
                            "label": "Private key",
                            "subLabel": "associated with your certificate"
                          }
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "doYouAlreadyHaveADIDForYourDomain": {
                        "title": "Do you already have a DID for your domain?",
                        "subtitle": "We couldn’t find a DID file linked to your domain. Please tell us what applies to you so we can continue.",
                        "options": {
                          "existingDid": {
                            "title": "Existing DID",
                            "description": "Yes, I have a DID but it's not in my directory yet"
                          },
                          "withoutDid": {
                            "title": "Without DID",
                            "description": "I don’t want to create a DID, show me another option"
                          },
                          "createDid": {
                            "title": "Create DID",
                            "description": "Help me create a DID file"
                          }
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "downloadChainAndDID": {
                        "title1": "Chain File",
                        "subtitle1": "Please download the new version of your chian file and keep it for the upcoming steps.",
                        "title2": "Your files are ready",
                        "subtitle2": "Please download and keep these files for the next step of your Gaia-X onboarding.",
                        "downloadButton": "Download",
                        "fileNames":{
                          "chain":"Certificate Chain",
                          "did":"DID File"
                        },
                        "fail": "Fail To upload",
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "verifyYourDidAndChainFiles": {
                        "title": "Verify your DID and chain files",
                        "subtitle": "Please place your files at the following addresses on your domain and then click Verify to check them.",
                        "verification": {
                          "button": {
                            "default": "Verify",
                            "loading": "Verifying...",
                            "success": "Verified!"
                          },
                          "notes": {
                            "title": "note:",
                            "error": "We couldn’t verify your DID or Chain. Make sure the files are available and try again."
                          }
                        },
                        "fields": {
                          "didFile": "DID File",
                          "chainFile": "Chain File"
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                      "letsCreateYourVerifiableCredentialsVCs": {
                        "title": "Let’s create your Verifiable Credentials (VCs)",
                        "subtitle": "Please review the information below and edit if needed before continuing.",
                        "sections": {
                          "participant": "Participant",
                          "legal": "Legal",
                          "termsAndConditions": "Terms and Conditions"
                        },
                        "inputs": {
                          "vcId": "VC ID",
                          "credentialSubjectId": "Credential Subject ID"
                        },
                        "note": {
                          "title": "note:",
                          "text": "Your onboarding is not finished yet. Signing these credentials is required to continue..."
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                    
                      "selectGaiaXDigitalClearingHouseVersion": {
                        "title": "Select Gaia-X Digital Clearing House Version",
                        "subtitle": "Choose the Gaia-X Digital Clearing House (GXDCH) version that fits your needs. Version 1 (Tagus) offers a quick start with basic rules, while Version 2 (Loire) provides stronger validation, more automation, and full alignment with the latest standards.",
                        "versions": {
                          "v1": {
                            "name": "Gaia-X Tagus",
                            "versionNumber": "Version 1.16.0",
                            "tag": "(Legacy)"
                          },
                          "v2": {
                            "name": "Gaia-X Loire",
                            "versionNumber": "Version 2.9.0",
                            "tag": "(Latest Version)"
                          },
                          "v3": {
                            "name": "Gaia-X Danube",
                            "note": "This version is not yet officially released by Gaia-X."
                          }
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "pleaseSelectYourClearingHouse": {
                        "title": "Please select your clearing house",
                        "subtitle": "Choose a Gaia-X Clearing House (GXCDH) to connect with for your onboarding.",
                        "options": {
                          "gaiax": "Gaia-X Lab",
                          "cispe": "CISPE",
                          "arsys": "Arsys",
                          "neustaAerospace": "Neusta Aerospace",
                          "aireNetwork": "Aire Networks",
                          "tsystem": "T-Systems",
                          "proximus": "Proximus",
                          "ovhCloud": "OVHcloud",
                          "aruba": "Aruba",
                          "deltaDao": "deltaDAO",
                          "pfalzkom": "PFALZKOM"
                        },
                        "nav": {
                          "previousStep": "PREVIOUS STEP",
                          "next": "NEXT"
                        },
                        "modal": {
                          "loadingTitle": "Please wait..."
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "yourVcFilesAreReadyToViewAndVerify": {
                        "title": "Your VC Files Are Ready To View And Verify",
                        "subtitle": "Please review the credentials below. You cannot modify them at this stage. To complete your onboarding, you need to sign them.",
                        "cards": {
                          "legal":{
                            "name": "Legal",
                            "action": "View JSON"
                          },
                          "participant":{
                            "name": "Participant",
                            "action": "View JSON"
                          },
                          "termsAndConditions":{
                            "name": "Terms and Conditions",
                            "action": "View JSON"
                          }
                        },
                        "note": {
                          "title": "note:",
                          "text": "If you're not sure, you can safely continue — you'll still be able to review your VCs later."
                        },
                        "nav": {
                          "previousStep": "Previous Step",
                          "next1": "Start Onboarding",
                          "next2": "Process"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                      "onboardingComplete": {
                        "title": "Your onboarding is complete 🎉",
                        "subtitle": "Congratulations! Your Gaia-X onboarding has been successfully completed.",
                        "fields": {
                            "name": "Onboarding Package",
                            "download":"Download",
                            "viewJson": "View JSON"
                          },
                        "nav": {
                          "previousStep": "Previous Step",
                          "next": "Next"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                      "termsAndConditionsOfParticipation": {
                        "title": "Terms and Conditions of Participation",
                        "subtitle": "Aviation Federation Demonstrator",
                        "conditions": {
                          "one":{
                            "heading": "1. Definitions",
                            "content":{
                                "title":"For the purposes of these Terms and Conditions (“Terms”):",
                                "rule1":{
                                    "bold":"“Federation”",
                                    "text":"means the Aviation Federation Demonstrator initiative established for the purposes described herein."
                                },
                                "rule2":{
                                    "bold":"“Participant”",
                                    "text":"means any organization or entity that has been accepted into the Federation through verified digital identity onboarding."
                                },
                                "rule3":{
                                    "bold":"“Data Sovereignty”",
                                    "text":"means the principle that each Participant retains full ownership, control, and responsibility for its data, subject to applicable law."
                                },
                                "rule4":{
                                    "bold":"“Verifiable Credentials (VCs)”",
                                    "text":"means digital attestations that support authentication, authorization, and governance under Self-Sovereign Identity (SSI) principles."
                                },
                                "rule5":{
                                    "bold":"“ABAC”",
                                    "text":"means Attribute-Based Access Control, a policy-based access management framework."
                                }
                    
                            }
                          },
                          "two":{
                            "heading": "2. Purpose",
                            "content": {
                                "title":"The Federation has been established to:",
                                "rule1":"1. Demonstrate secure, trusted, and interoperable collaboration in the aviation sector.",
                                "rule2":"2. Apply federated architecture principles and the Gaia-X Trust Framework to ensure trust anchoring, compliance assessment, and governance.",
                                "rule3":"3. Enable Participants to share data securely without loss of data control.",
                                "rule4":"4. Implement Zero Trust security, SSI-based authentication, and verifiable authorization in real-world scenarios such as Aircraft on Ground (AOG) procedures."
                            }
                          },
                          "three":{
                            "heading": "3. Eligibility and Onboarding",
                            "content": {
                                "rule1":"3.1 Participation is subject to successful digital identity verification in compliance with the Federation’s onboarding requirements and Gaia-X Trust Framework.",
                                "rule2":"3.2 Participants must accept and comply with these Terms prior to joining.",
                                "rule3":"3.3 The Federation reserves the right to approve, reject, suspend, or terminate a Participant’s involvement at its sole discretion if obligations are breached."
                            }
                          },
                          "four":{
                            "heading": "4. Rights and Obligations of Participants",
                            "content": {
                                "rule1":"4.1 Data Control",
                                "rule2":"• Each Participant retains full control and responsibility for its own data.",
                                "rule3":"• Sensitive data shall not be centralized; all access shall be governed through federated mechanisms.",
                                "rule4":"4.2 Security and Access Management",
                                "rule5":"• Participants shall implement and adhere to Zero Trust and ABAC practices.",
                                "rule6":"• All authentication and authorization shall utilize verifiable credentials, with runtime verification where applicable.",
                                "rule7":"• Participants must promptly revoke compromised credentials and report suspected security incidents.",
                                "rule8":"4.3 Service Publication and Consumption",
                                "rule9":"• Participants may publish services to the shared catalogue in compliance with federation rules and interoperability standards.",
                                "rule10":"• Participants consuming services are responsible for ensuring compliance with applicable laws and contract requirements."
                            }
                          },
                          "five":{
                            "heading": "5. Compliance and Audit",
                            "content": {
                                "rule1":"5.1 Participants agree to comply with applicable aviation, cybersecurity, and data protection regulations.",
                                "rule2":"5.2 All interactions within the Federation shall be logged, auditable, and subject to review for compliance.",
                                "rule3":"5.3 The Federation may conduct verification or compliance assessments as necessary to preserve trust."
                            }
                          },
                          "six":{
                            "heading": "6. Confidentiality",
                            "content": {
                                "rule1":"6.1 Participants shall treat as confidential all non-public information exchanged within the Federation, unless disclosure is required by law.",
                                "rule2":"6.2 Obligations of confidentiality remain in force during and after termination of participation."
                            }
                          },
                          "seven":{
                            "heading": "7. Liability and Indemnity",
                            "content": {
                                "rule1":"7.1 Each Participant is solely responsible for its data, actions, and use of Federation services.",
                                "rule2":"7.2 The Federation and its governing entities shall not be liable for any indirect, incidental, or consequential damages arising from participation.",
                                "rule3":"7.3 Participants shall indemnify and hold harmless the Federation and other Participants against claims, damages, or losses arising from their non-compliance, misuse of credentials, or data mismanagement."
                            }
                          },
                          "eight":{
                            "heading": "8. Termination",
                            "content": {
                                "rule1":"8.1 Participation may be terminated by either party with written notice, subject to compliance with outstanding obligations.",
                                "rule2":"8.2 The Federation may immediately suspend or terminate a Participant’s access in cases of:",
                                "rule3":"• Security or compliance breaches,",
                                "rule4":"• Misuse of verifiable credentials,",
                                "rule5":"• Violation of sovereignty or confidentiality obligations."
                            }
                          },
                          "nine":{
                            "heading": "9. Governing Law and Jurisdiction",
                            "content":"These Terms shall be governed by and construed in accordance with the laws of [insert governing jurisdiction]. Any disputes arising shall be subject to the exclusive jurisdiction of the competent courts in [insert location]."
                          },
                          "ten":{
                            "heading": "10. Amendments",
                            "content": "The Federation reserves the right to update or amend these Terms. Participants will be notified of changes in advance, and continued participation shall constitute acceptance."
                            
                          },
                          "eleven":{
                            "heading": "11. Entire Agreement",
                            "content": "These Terms represent the entire agreement between the Federation and the Participant regarding participation in the demonstrator and supersede any prior agreements or understandings."
                          }
                        },
                        "checkbox": "I hereby agree to the terms and conditions of aviation and government.",
                        "nav": {
                          "previousStep": "Previous Step",
                          "next": "Next"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                      "createAviationVerifiableCredentials": {
                        "title": "Let's create your Aviation Verifiable Credentials (VCs)",
                        "subtitle": "Please review the VC ID and Credential Subject ID for your Aviation participant before proceeding.",
                        "heading":"Aviation participant",
                        "vcId": "VC ID",
                        "credentialSubjectId": "Credential Subject ID",
                        "nav": {
                          "previousStep": "Previous Step",
                          "next": "Next"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                    
                      "aviationOnboardingComplete": {
                        "title": "Your onboarding on Aviation Federation is complete",
                        "subtitle": "Congratulations! You've successfully completed the Aviation Federation onboarding process.",
                        "save": "Save to my PCM",
                        "download": "Download package & add to PCM",
                        "nav": {
                          "previousStep": "Previous Step",
                          "finish": "Finish"
                        },
                        "help": {
                          "text": "Having troubles?",
                          "linkLabel": "Get Help"
                        }
                      },
                      "loaders": {
                        "loader1": {
                          "flipTexts":{ 
                            "one":"Fetching your company information",
                            "two":"Discovering companies on the web",
                            "three":"Collecting public profiles and metadata",
                            "four":"Verifying and analyzing gathered data for accuracy",
                            "five":"Rendering results"
                          },
                          "subtitle": "This may take a few moments. We're looking up your company on public networks."
                        },
                        "loader2": {
                          "title": "Updating your profile records",
                          "subtitle": "Your profile details are being processed and securely stored. This ensures it remains accurate within the system."
                        },
                        "loader3": {
                          "title1": "Calling",
                          "title2": "compliance",
                          "subtitle": "The Clearing House is issuing your Verifiable Credential."
                        },
                        "loader4": {
                          "title": "Signing your credentials",
                          "subtitle": "We're securely signing your Airbus Verifiable Credentials. This may take a few seconds."
                        }
                      }
                    },
            isCategory: false

          
          
          
        };
    },

    watch: {
        'companyData.legalIdentifiers.euVatId': function () {
            this.WatchLegalIdentifiers();
        },
        'companyData.headquartersAddress.legalAddressIso': function () {
            this.WatchLegalIdentifiers();
        }
    },
    computed: {
       allSuccessful() {
          return Object.values(this.uploadStatuses).every(status => status === 'completed');
        },
       allVerified() {
            return this.DIDButtonState === 'success' && this.ChainButtonState === 'success';
        }
    },
    methods: {
     
        getCookie: function (name) {
            let value = "; " + document.cookie;
            let parts = value.split("; " + name + "=");
            if (parts.length == 2) return parts.pop().split(";").shift();
        },
      
        openJsonPopup(jsonData) {
            this.currentJson = jsonData; // save selected JSON
            const pretty = JSON.stringify(jsonData || {}, null, 2);
        
            this.showJson = true;
            this.$nextTick(() => {
              const block = document.getElementById('jsonBlock');
              if (block) {
                block.textContent = pretty;
                if (window.Prism && typeof Prism.highlightElement === 'function') {
                  Prism.highlightElement(block);
                }
              }
            });
          },
        
          downloadJSON() {
            if (!this.currentJson) return;
        
            const text = JSON.stringify(this.currentJson, null, 2);
            const blob = new Blob([text], { type: "application/json" });
            const url = URL.createObjectURL(blob);
        
            const a = document.createElement("a");
            a.href = url;
            a.download = "file.json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        
            URL.revokeObjectURL(url);
          },
        
          copyJSON() {
            if (!this.currentJson) return;
        
            const text = JSON.stringify(this.currentJson, null, 2);
            const nav = window.navigator;
        
            if (nav && nav.clipboard && typeof nav.clipboard.writeText === 'function') {
              nav.clipboard.writeText(text)
                .then(() => this.onCopied?.())
                .catch(() => this.fallbackCopy(text));
            } else {
              this.fallbackCopy(text);
            }
          },


        fallbackCopy(text) {
          const ta = document.createElement('textarea');
          ta.value = text;
          ta.setAttribute('readonly', '');
          ta.style.position = 'fixed';
          ta.style.top = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          try {
            document.execCommand('copy');
            this.onCopied?.() || alert('✅ JSON copied');
          } catch (e) {
            console.error('Copy failed:', e);
            alert('❌ Copy failed');
          } finally {
            document.body.removeChild(ta);
          }
        },
     
        
        async startTransformation() {
          if (this.isAnimating) return;
          
          this.isAnimating = true;
          
          // Step 1: Fade out onboarding content
          this.isFadingOut = true;
          
          await this.delay(400);
          
          // Step 2: Start expanding animation
          this.isExpanding = true;
          
          await this.delay(800);
          
          // Step 3: Mark as expanded and switch content
          this.isExpanded = true;
          
          
          await this.delay(100);
          
          // Step 4: Fade in form content
          this.isFadingIn = true;
          
          await this.delay(500);
          
          this.isAnimating = false;
        },
        async goNextStep() {
          if (this.isAnimating) return;
          
          this.isAnimating = true;
          
          // Step 1: Fade out form content first
          this.isFadingOut = true;
          
          await this.delay(400);
          
          // Step 2: Switch content and start shrinking
          this.isExpanding = false;
          this.isExpanded = false;
          
          await this.delay(800);
          
          // Step 3: Reset fade states
          this.isFadingOut = false;
          
          await this.delay(100);
          
          // Step 4: Fade in success content
          this.isFadingIn = true;
          
          await this.delay(500);
          
          this.isAnimating = false;
        },
        
        restartProcess() {
          // Reset all states
          this.currentStep = 'pg1';
          this.isAnimating = false;
          this.isFadingOut = false;
          this.isFadingIn = false;
          this.isExpanding = false;
          this.isExpanded = false;
          
          // Reset form states
          this.showCompanyType = true;
          this.showState = false;
          this.showLeftWhite = false;
        },
        
        goToNextStep() {
          this.showCompanyType = false;
          this.showState = true;
        },
        
        onLeftBoxLeave() {
          this.showLeftWhite = true;
          this.showState = true;
        },
        
        addDirector() {
          this.directors.push({ firstName: '', lastName: '' });
        },
        
        removeDirector(index) {
          this.directors.splice(index, 1);
        },
        
        addOfficer() {
          this.officers.push({ firstName: '', lastName: '' });
        },
        
        removeOfficer(index) {
          this.officers.splice(index, 1);
        },
        
        hasData(section) {
          if (!section || typeof section !== "object") return false;
          return Object.values(section).some(value => {
            if (Array.isArray(value)) return value.length > 0;
            return value !== null && value !== "";
          });
        },
        
        delay(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        },
        setupDropdown(selector) {
          const question = document.querySelector(selector);
          const submittedEl = question.querySelector('.submitted-value');
          const dropdownText = question.querySelector('.dropdown-text');
    
          question.querySelectorAll('.dropdown-option').forEach(option => {
            option.addEventListener('click', () => {
              const value = option.dataset.value;
    
              // Update DOM
              submittedEl.textContent = value;
              submittedEl.style.display = 'inline';
              dropdownText.textContent = option.innerText.trim();
    
              // Save to Vue data
              this.answers[question.id] = value;
              console.log(`${question.id}:`, value);
              
    
              // Show next question
              this.showNextQuestion(question.id);
            });
          });
        },
    
        // 🔹 Setup Q2–Q5 to submit on Enter or arrow click
        setupTextQuestions(selectors) {
          selectors.forEach(selector => {
            const question = document.querySelector(selector);
            const input = question.querySelector('.inline-input');
            const arrow = question.querySelector('.input-arrow');
            const submittedEl = question.querySelector('.submitted-value');
    
            if (!input || !arrow) return;
    
            const submitAnswer = () => {
              const value = input.value.trim();
              if (!value) return; // Skip if empty
    
              // Update DOM
              submittedEl.textContent = value;
              submittedEl.style.display = 'inline';
    
              // Save to Vue data
              this.answers[question.id] = value;
              console.log(`${question.id}:`, value);
    
              // Show next question
              this.showNextQuestion(question.id);
            };
    
            // 🔹 Click on arrow
            arrow.addEventListener('click', submitAnswer);
    
            // 🔹 Press Enter
            input.addEventListener('keydown', (e) => {
              if (e.key === 'Enter') {
                e.preventDefault(); // prevent form submission if inside a form
                submitAnswer();
              }
            });
          });
        },
    
        // 🔹 Show next question dynamically
        showNextQuestion(currentId) {
          const currentNumber = parseInt(currentId.replace('question', ''));
          const nextNumber = currentNumber + 1;
          const nextQuestion = document.querySelector(`#question${nextNumber}`);
          if (nextQuestion) {
            nextQuestion.style.display = 'block';
          }
        },
        sendInformation() {
          
          console.log('this awnser'+this.answers.question1)
          if (this.answers.question1 === "available") {
              
              
              this.notAvailable= true;
              
              uibuilder.send({
                data:{
                    topic: 'company.information',
                    session:{
                        stage: this.currentStep,
                        "sessionId":this.getCookie('sid'),
                        "clientId":this.getCookie('uibuilder-client-id')
                    },
                    recordDetails: {
                        companyInformation: {
                            availability: this.answers.question1,
                            domain: this.answers.question2,
                            onboardingDomain: this.answers.question4
                        }
                    }
                }
              })
            } else {
                
              this.notAvailable= true;    
                
              uibuilder.send({
                data:{
                    topic: 'company.information',
                    session:{
                    stage: this.currentStep,
                  "sessionId":this.getCookie('sid'),
                  "clientId":this.getCookie('uibuilder-client-id')
                },
                recordDetails:{
                    companyInformation: {
                      availability: this.answers.question1,
                      onboardingDomain: this.answers.question4,
                      legalName: this.answers.question3,
                      engagedIn: this.answers.question5
                    }
                }
                }
              });
            } 
            
            this.currentStep = 'loader1';
        },
        sendEditedData(){
          console.log('Sending updated company data:', this.companyData)
          uibuilder.send({
                data:{
                    topic: ' ',
                    session:{
                        stage: this.currentStep,
                        "sessionId":this.getCookie('sid'),
                        "clientId":this.getCookie('uibuilder-client-id')
                    },
                    recordDetails: {
                        companyProfile: this.companyData
                    }
                }
            })
            this.currentStep = 'loader2';
            this.goNextStep();
            this.isExpanded = false
            
        },
        checkLegalIdentifiers() {
          const vatId = this.companyData?.legalIdentifiers?.euVatId || '';
          const legalAddressIso = this.companyData?.headquartersAddress?.legalAddressIso || '';
        
       
          const vatFilled = vatId.trim() !== '';
          const legalAddressFilled = legalAddressIso.trim() !== '';
        
          this.allFilledData = vatFilled && legalAddressFilled;
        
          if (this.allFilledData) {
            this.sendEditedData();
          } else {
            this.editCompanyDetails = true;
          }
        },
        WatchLegalIdentifiers() {
              const vatId = this.companyData?.legalIdentifiers?.euVatId || '';
              const legalAddress = this.companyData?.headquartersAddress?.legalAddressIso || '';
              
              this.allFilledData = vatId.trim() !== '' && legalAddress.trim() !== '';
        },

        setupFileUploadListeners() {
           
            const uploadCards = document.querySelectorAll('.upload-card');
            const bundleInput = document.getElementById('bundle-file');
            const certInput = document.getElementById('certificate-file');
            const keyInput = document.getElementById('private-key-file');
            
         
            if (uploadCards[0]) {
                uploadCards[0].addEventListener('click', () => {
                    bundleInput.click();
                });
            }
            
            if (bundleInput) {
                bundleInput.addEventListener('change', (e) => {
                    this.handleFileUpload(e, 'bundle');
                });
            }
            
         
            if (uploadCards[1]) {
                uploadCards[1].addEventListener('click', () => {
                    certInput.click();
                });
            }
            
            if (certInput) {
                certInput.addEventListener('change', (e) => {
                    this.handleFileUpload(e, 'certificate');
                });
            }
            
        
            if (uploadCards[2]) {
                uploadCards[2].addEventListener('click', () => {
                    keyInput.click();
                });
            }
            
            if (keyInput) {
                keyInput.addEventListener('change', (e) => {
                    this.handleFileUpload(e, 'privateKey');
                });
            }
        },
         handleFileUpload(event, type) {
          const file = event.target.files[0];
          if (!file) return;
        
          this.uploadStatuses[type] = 'uploading';
        
          const reader = new FileReader();
          reader.onload = () => {
            const base64Data = reader.result.split(',')[1];
        
            // store the file temporarily so we can bundle them later
            if (!this.uploadedFiles) this.uploadedFiles = {};
            this.uploadedFiles[type] = {
              filetype: type,
              fileName: file.name,
              fileContent: base64Data,
              result: "none"
            };
        
            // send immediately (keep old behavior)
            console.log("tak mifresti")
            uibuilder.send({
              data: {
                topic: 'allCertificates',
                session: {
                  stage: this.currentStep,
                  step:2,
                  sessionId: this.getCookie('sid'),
                  clientId: this.getCookie('uibuilder-client-id')
                },
                recordDetails: {
                  files: this.uploadedFiles[type],
                  companyProfile: this.companyData
                }
              }
            });
        
          };
          reader.readAsDataURL(file);
        },
        
        updateUploadStatus(type, status) {
          this.uploadStatuses[type] = status; 
        },
        
        statusClass(type) {
          return {
            none: this.uploadStatuses[type] === 'none',
            uploading: this.uploadStatuses[type] === 'uploading',
            completed: this.uploadStatuses[type] === 'completed',
            alert: this.uploadStatuses[type] === 'alert'
          };
        },
        
        statusText(type) {
          const map = {
            none: 'File Upload',
            uploading: 'Uploading...',
            completed: 'File Upload',
            alert: 'File Upload'
          };
          return map[this.uploadStatuses[type]];
        },
        
        // NEW function: send ALL uploaded files together
        sendAllCertificates() {
        console.log("hurraaaay frontend")
          if (!this.uploadedFiles || Object.keys(this.uploadedFiles).length === 0) {
            alert("No files uploaded yet!");
            return;
          }
        
          uibuilder.send({
            data: {
              topic: 'allCertificates',
              session: {
                stage: this.currentStep,
                step: 2,
                sessionId: this.getCookie('sid'),
                clientId: this.getCookie('uibuilder-client-id')
              },
              recordDetails: {
                files: this.uploadedFiles, // send all uploaded files at once
                companyProfile: this.companyData
              }
            }
          });
        
          console.log("All certificates sent:", this.uploadedFiles);
        },
        
        confirmUploads() {
          this.sendAllCertificates();
        },
        updateConfirmButton() {
            const confirmButton = document.querySelector('.correct-button');
            if (confirmButton) {
                if (this.allFilesUploaded) {
                    confirmButton.disabled = false;
                    confirmButton.classList.remove('disabled');
                    console.log('Button enabled - all files uploaded');
                } else {
                    confirmButton.disabled = true;
                    confirmButton.classList.add('disabled');
                    console.log('Button disabled - not all files uploaded');
                }
            }
        },
        handleNextCertificate() {
            if (this.selectedCertificate === 'no-access') {
              uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            certificate: "redbox"
                        }
                    }
                })
            } 
            else if (this.selectedCertificate === 'extended-validation') {
             this.showStateB = true; 
             this.showStateA= false;
             
            } 
            else if (this.selectedCertificate === 'dv-ov') {
              this.certificatePopUp = "right"
            } 
            else {
              alert('Please select an option before continuing.');
            }
        },
        handleNextDomain() {
            if (this.selectedDID === 'no-access') {
              this.showBusinessDetailsA = false;
              this.showBusinessDetailsB= true;
              this.hasdomain= true;
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:3,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            certificate: "",
                            downloadFiles: {
                                chain:""
                            },
                            companyProfile: this.companyData
                        }
                    }
                })
            } 
            else if (this.selectedDID === 'extended-validation') {
             this.showBusinessDetailsA = false;
             this.showBusinessDetailsB= true;
             this.hasdomain= false;
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:3,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            certificate:"",
                            downloadFiles: {
                                chain:"",
                                did:""
                            }
                        }
                    }
                })
            } 
            else if (this.selectedDID === 'dv-ov') {
              uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:3,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            certificate: "redbox"
                        }
                    }
                })
            } 
            else {
              alert('Please select an option before continuing.');
            }
        },
        handleNextURL() {
            
            
                this.showBusinessDetailsB = false; 
                this.showBusinessDetailsC= true;
                this.loadVerify = false;
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:3,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            certificate: "",
                            urls: {
                                
                            },

                        }
                    }
                })
 
        },
        handleNextVerify(which) {
            
            
                const key = which + 'ButtonState'; // e.g. "DIDButtonState" or "ChainButtonState"
    
                if (this[key] !== 'default') return;
            
                this[key] = 'loading';
                this.verifyError = false;
                
                if ( which === "DID") {
                    uibuilder.send({
                        data:{
                            topic: ' ',
                            session:{
                                stage: this.currentStep,
                                step:3,
                                "sessionId":this.getCookie('sid'),
                                "clientId":this.getCookie('uibuilder-client-id')
                            },
                            recordDetails: {
                                companyProfile:this.companyData,
                                urls: {
                                    didUrl: this.didURL
                                },
    
                            }
                        }
                    })
                }
                if ( which === "Chain") {
                    uibuilder.send({
                        data:{
                            topic: ' ',
                            session:{
                                stage: this.currentStep,
                                step:3,
                                "sessionId":this.getCookie('sid'),
                                "clientId":this.getCookie('uibuilder-client-id')
                            },
                            recordDetails: {
                                companyProfile:this.companyData,
                                urls: {
                                    chainUrl: this.chainURL
                                },
    
                            }
                        }
                    })
                }
                
 
        },
        handleNextVerifiable() {
            
                this.showTeamA = true; 
                this.showBusinessDetailsC= false;
                this.loadVC = false;
            
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:4,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            ids: {
                                
                            },

                        }
                    }
                })
 
        },
        handleNextCredentials() {
            
                this.showTeamD = true; 
                this.showTeamA= false;
            
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:4,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            ids: this.formData,

                        }
                    }
                })
 
        },
        handleNextVersion() {
            
                this.showTeamB = true; 
                this.showTeamD= false;
                this.loadClearing = false;
            
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:4,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            companyProfile:this.companyData,
                            versionCompliance: this.versionCompliance,
                            clearingHouseList: "",
                            

                        }
                    }
                })
 
        },
        handlePreviousVersion() {
            
               this.showTeamB = false; 
               this.showTeamD= true;
                
               this.pfalzkom = false;
               this.gaiax = false ;
               this.deltaDao = false ;
               this.aruba = false ;
               this.ovhCloud = false ;
               this.proximus = false ;
               this.tsystem = false ;
               this.aireNetwork = false ;
               this.neustaAerospace = false ;
               this.cispe = false ;
               this.arsys = false ;
                
        },
        handleNextClearing() {
            
                this.showTeamB = false; 
                this.showTeamC= true;
                this.loadVCJson= false;
            
                uibuilder.send({
                    data:{
                        topic: ' ',
                        session:{
                            stage: this.currentStep,
                            step:4,
                            "sessionId":this.getCookie('sid'),
                            "clientId":this.getCookie('uibuilder-client-id')
                        },
                        recordDetails: {
                            vcs:"",
                            selectedClearingHouse: this.selectedClearingHouse,
                            versionCompliance: this.versionCompliance,

                        }
                    }
                });
 
        },
        handleNextVP() {
            
                this.showTeamC = false; 
                this.showCompletion= true;

            
            //   setTimeout(() => {
            //     uibuilder.send({
            //         data:{
            //             topic: ' ',
            //             session:{
            //                 stage: this.currentStep,
            //                 step:4,
            //                 "sessionId":this.getCookie('sid'),
            //                 "clientId":this.getCookie('uibuilder-client-id')
            //             },
            //             recordDetails: {
            //                 vcs: {
            //                     participantVC: this.participantVC,
            //                     termsAndConditionsVC: this.termsAndConditionsVC,
            //                     legalVC: this.legalVC
            //                 }

            //             }
            //         }
            //     });
            //     }, 4000);
                // setTimeout(() => {
                    
                     uibuilder.send({
                        data:{
                            topic: ' ',
                            session:{
                                stage: "pg3",
                                step:5,
                                "sessionId":this.getCookie('sid'),
                                "clientId":this.getCookie('uibuilder-client-id')
                            },
                            recordDetails: {
                                vp:"",
                                versionCompliance: this.versionCompliance,
    
                            }
                        }
                    });
                // }, 8000);
                
                this.currentStep = "loader3";
                this.goNextStep();
 
        },
        handleNextAviation() {
            
                this.showCompletionC = false; 
                this.showCompletionD= true;
                this.currentStep = "loader4";
                this.goNextStep();
                setTimeout(() => {
                    this.currentStep = 'pg3';
                    this.startTransformation();
                    
                }, 5000);
 
        },
        statusIcon(type) {
          const status = this.uploadStatuses[type];
          switch (status) {
            case 'uploading':
              return `<svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                            <circle cx="12" cy="12" r="3" fill="currentColor">
                                <animate attributeName="r" values="3;5;3" dur="1s" repeatCount="indefinite"/>
                                <animate attributeName="opacity" values="1;0.5;1" dur="1s" repeatCount="indefinite"/>
                            </circle>
                        </svg>`;
            case 'completed':
              return `<svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                        </svg>`;
            case 'alert':
              return `<svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>`;
            default: // 'none'
              return `<svg width="24" height="24" fill="none" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10" stroke="#9ca3af" stroke-width="2"/>
                        <path d="M9 12h6" stroke="#9ca3af" stroke-width="2"/>
                      </svg>`;
          }
        },
        createFileUrl(base64) {
          try {
            // Convert base64 string to binary
            const cleanBase64 = base64.trim()
            const byteCharacters = atob(cleanBase64)
            const byteNumbers = new Array(byteCharacters.length)
            for (let i = 0; i < byteCharacters.length; i++) {
              byteNumbers[i] = byteCharacters.charCodeAt(i)
            }
            const byteArray = new Uint8Array(byteNumbers)
    
            // Create Blob & URL
            const blob = new Blob([byteArray], { type: 'application/x-pem-file' })
            return URL.createObjectURL(blob)
          } catch (error) {
            console.error('Invalid base64 received:', error)
            return null
          }
        },
        downloadFile(url, fileName) {
          if (!url) {
            alert('File not ready to download yet! Please try again after a few seconds.')
            return
          }
          const a = document.createElement('a')
          a.href = url
          a.download = fileName
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
        },
        
        toggleChat() {
            this.isOpen = !this.isOpen;
            if (this.isOpen) {
              
                if (!this.ws || this.ws.readyState > 1) {
                    this.connectWebSocket();
                }
                this.$nextTick(() => {
                    const input = document.querySelector('.message-input');
                    if (input) input.focus();
                });
            }
        },
        
        closeChat() {
            this.isOpen = false;
        },
        
        connectWebSocket() {
            
            const WS_URL = (location.protocol === 'https:' ? 'wss://' : 'ws://') + 
                          location.host + '/onboarding/ws/chat';
            
            try {
                this.ws = new WebSocket(WS_URL);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const msg = JSON.parse(event.data);
                        if (msg.text) {
                            this.addMessage(msg.text, 'bot');
                        }
                    } catch (e) {
                        
                        this.addMessage(String(event.data), 'bot');
                    }
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;

                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket Error:', error);
                    this.addMessage('WebSocket Error', 'bot');
                };
                
            } catch (error) {
                console.error('Connection Error:', error);
                this.addMessage('Connection Error', 'bot');
            }
        },
        
        sendMessage() {
            if (!this.userInput.trim()) return;
           this.addMessage(this.userInput.trim(), 'user');
            const userMessage = this.userInput.trim();
             if (this.ws && this.ws.readyState === 1) {
                 this.ws.send(JSON.stringify({ text: userMessage }));
            } else {
                setTimeout(() => {
                    this.simulateBotResponse(userMessage);
                }, 1000);
            }
            
            this.userInput = '';
        },
        
        addMessage(content, type) {
            this.messages.push({
                id: this.messageId++,
                content: content,
                type: type,
                time: new Date()
            });
            
            this.$nextTick(() => {
                const container = this.$refs.messagesContainer;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },
        
        async simulateBotResponse(userMessage) {
            const response = await this.getAIResponse(userMessage);
            this.addMessage(response, 'bot');
        },
        
        async getAIResponse(userMessage) {
            return 'Got Disconnected. Please try to open the chatbot again.';
        },
        
        selectSuggestion(event) {
            const suggestion = event.currentTarget;
            const title = suggestion.querySelector('h4').textContent;
            this.userInput = title;
            this.sendMessage();
        },
        
        formatTime(date) {
            return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        },
        isMobile() {
           return window.innerWidth < 768;
        },
    
        handleMobileClick() {
            if (this.isMobile()) {
              alert("Please try again in desktop.");
              window.location.reload();
            } 
        }
        

      },

    mounted() {
        
        uibuilder.start();
        
        var vueApp = this

        uibuilder.onChange('msg', function (msg) {
            
            vueApp.animations = vueApp.animations || {};
             
    //--------------------sessioninit node setups------------------------------------------------------ / start 
    
    
            if (msg.launch) {
                vueApp.launch = msg.launch
                console.log(msg.launch) 
            }
            
            
            
            if (msg.rocket && !vueApp.animations.rocket) {
              if (vueApp.$refs.lottieContainer) {
                vueApp.animations.rocket = lottie.loadAnimation({
                    container: vueApp.$refs.lottieContainer,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: msg.rocket
                });
              }
            }
            
            if (msg.signing && !vueApp.animations.signing) {
              if (vueApp.$refs.signingContainer) {
                vueApp.animations.signing = lottie.loadAnimation({
                  container: vueApp.$refs.signingContainer,
                  renderer: 'svg',
                  loop: true,
                  autoplay: true,
                  animationData: msg.signing
                });
              }
            }
            if (msg.signing2 && !vueApp.animations.signing2) {
              if (vueApp.$refs.signingContainer2) {
                vueApp.animations.signing2 = lottie.loadAnimation({
                  container: vueApp.$refs.signingContainer2,
                  renderer: 'svg',
                  loop: true,
                  autoplay: true,
                  animationData: msg.signing2
                });
              }
            }
            
            if (msg.loader1 && !vueApp.animations.loader1) {
              if (vueApp.$refs.loaderContainer) {
                vueApp.animations.loader1 = lottie.loadAnimation({
                    container: vueApp.$refs.loaderContainer,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: msg.loader1
                });
              }
            }
            
            if (msg.loader2 && !vueApp.animations.loader2) {
              if (vueApp.$refs.loader2Container) {
                vueApp.animations.loader2 = lottie.loadAnimation({
                  container: vueApp.$refs.loader2Container,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: msg.loader2
                });
              }
            }
            
            if (msg.lottiebox && !vueApp.animations.lottiebox) {
              if (vueApp.$refs.dataContainer) {
                vueApp.animations.lottiebox = lottie.loadAnimation({
                    container: vueApp.$refs.dataContainer,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: msg.lottiebox
                });
              }
            }
    //--------------------sessioninit node setups------------------------------------------------------// finish
    
    //--------------------check BACKend outputs------------------------------------------------------ / start 
            if (msg.category) {
                vueApp.category = msg.category;
                console.log(vueApp.category);
            }
            
            if(msg?.data?.errorComplience){
               window.alert(msg.data.errorComplience.errorMessage);
               vueApp.showTeamB = true;
               vueApp.showCompletion= false;
               vueApp.participantVC = "";
               vueApp.legalVC = "";
               vueApp.termsAndConditionsVC = "";
               vueApp.currentStep = "pg3";
               vueApp.startTransformation;
               
            }
            if(msg?.data?.errorVC){
               window.alert(msg.data.errorVC.errorMessage);
               vueApp.showTeamB = true;
               vueApp.showTeamC = false;
               
            }
            if (msg?.data?.recordDetails?.ids?.lrnVCid) {
              vueApp.loadVC = true;    
              vueApp.formData = { ...msg?.data?.recordDetails?.ids};
              console.log("Form data updated:", vueApp.formData);
            }
            
            console.log("the vcs:", msg?.data?.recordDetails?.vcs)
            if (msg?.data?.recordDetails?.vcs) {
               vueApp.loadVCJson = true;
               vueApp.participantVC = msg.data.recordDetails.vcs.participantVC;
               vueApp.legalVC = msg.data.recordDetails.vcs.legalVC;
               vueApp.termsAndConditionsVC = msg.data.recordDetails.vcs.termsAndConditionsVC;
               console.log(vueApp.legalVC)
               console.log(vueApp.termsAndConditionsVC)
               console.log(vueApp.participantVC)
               
            }
            if (msg?.data?.recordDetails?.vp) {
            
               vueApp.onboardingPackage = msg.data.recordDetails.vp.json;
               console.log(vueApp.onboardingPackage)
               
            }
          
            if(msg?.data?.session?.stage=='pg1'){
                // window.location.reload();
            }
            if (msg.isExpanded === true && vueApp.isExpanded === false) {
                vueApp.startTransformation()
            } else if (msg.isExpanded === false && vueApp.isExpanded === true) {
                vueApp.goNextStep()
            }
            if (msg?.data?.session?.stage && msg?.data?.session?.stage !== vueApp.currentStep) {
                 setTimeout(() => {
                    vueApp.currentStep = msg.data.session.stage;
                    
                }, 1700);
                document.cookie = "sid=" + msg.data.session.sessionId + ";path=/;max-age=3600"; 
            }
            if (msg?.data?.session?.stage === 'pg2') {
                vueApp.companyData = msg.data.recordDetails.companyProfile; 
            }
            
            
            if (msg?.data?.recordDetails?.files) {
              const { filetype, result } = msg.data.recordDetails.files;
            
              if (filetype === 'certificate') {
                vueApp.uploadStatuses.certificate = result;
              }
              else if (filetype === 'bundle') {
                vueApp.uploadStatuses.bundle = result;
              }
              else if (filetype === 'privateKey') {
                vueApp.uploadStatuses.privateKey = result;
              }
            
              console.log('Updated uploadStatuses:', vueApp.uploadStatuses);
            }
            if (msg?.data?.recordDetails?.downloadFiles) {
            
               const files = msg.data.recordDetails.downloadFiles;
        


                if (files.chain.fileContent) {
                  vueApp.chainUrl = vueApp.createFileUrl(files.chain.fileContent)
                  vueApp.chainFileName = files.chain.fileName
                }
        
                // Prepare DID File
                if (files.did.fileContent) {
                  vueApp.didUrl = vueApp.createFileUrl(files.did.fileContent)
                  vueApp.didFileName = files.did.fileName
                }
            }
            
            
            
            if (msg?.data?.recordDetails?.urls?.didUrl) {
               vueApp.loadVerify = true;
               vueApp.didURL = msg.data.recordDetails.urls.didUrl;
            }
            if (msg?.data?.recordDetails?.urls?.chainUrl) {
                
               vueApp.loadVerify = true;
               vueApp.chainURL = msg.data.recordDetails.urls.chainUrl;
            }
            if (msg?.data?.recordDetails?.urls?.didUrl && msg?.data?.recordDetails?.urls?.state) {
                
                if(msg.data.recordDetails.urls.state === "success") {
                    vueApp.DIDButtonState= msg.data.recordDetails.urls.state
                    
                } else if (msg.data.recordDetails.urls.state === "failed") {
                    
                    vueApp.DIDButtonState= "default";
                    vueApp.verifyError= true;
                }
            
               
            }
            if (msg?.data?.recordDetails?.urls?.chainUrl && msg?.data?.recordDetails?.urls?.state) {
            
               
               if(msg.data.recordDetails.urls.state === "success") {
                    vueApp.ChainButtonState= msg.data.recordDetails.urls.state
                    
                } else if (msg.data.recordDetails.urls.state === "failed") {
                    
                    vueApp.ChainButtonState= "default";
                    vueApp.verifyError= true;
                }
            }
            if (msg?.data?.recordDetails?.clearingHouseList) {
               vueApp.loadClearing = true; 
               const clearing = msg.data.recordDetails.clearingHouseList ;
               vueApp.pfalzkom = clearing.pfalzkom ;
               vueApp.gaiax = clearing.gaiax ;
               vueApp.deltaDao = clearing.deltaDao ;
               vueApp.aruba = clearing.aruba ;
               vueApp.ovhCloud = clearing.ovhCloud ;
               vueApp.proximus = clearing.proximus ;
               vueApp.tsystem = clearing.tsystem ;
               vueApp.aireNetwork = clearing.aireNetwork ;
               vueApp.neustaAerospace = clearing.neustaAerospace ;
               vueApp.cispe = clearing.cispe ;
               vueApp.arsys = clearing.arsys ;
               
            }
            
          console.log(vueApp.didFileName)
          console.log(vueApp.chainFileName)
          console.log(vueApp.DIDButtonState)
          console.log(vueApp.ChainButtonState)
          console.log(msg.isExpanded) 


//--------------------check BACKend outputs------------------------------------------------------// finish                           
        })

        
        vueApp.setupDropdown('#question1');
        vueApp.setupTextQuestions(['#question2', '#question3', '#question4', '#question5']);
        vueApp.setupFileUploadListeners();
        vueApp.updateConfirmButton();
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
        
        
    },
    beforeUnmount() {
       
        if (this.ws) {
            this.ws.close();
        }
    }
})

app.mount('#app')
