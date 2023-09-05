import React, { Component } from 'react';
import {requestAPI} from "../handler";
import {Dialog, showDialog} from "@jupyterlab/apputils";
import {
    LOGIN2_BUTTON_CLASS,
    LOGIN2_DIALOG_CLASS,
    LOGIN2_INPUT_CLASS,
    LOGIN_BUTTON_LABEL,
} from "../utils";

// Enum representing different states of authentication
enum AuthStatus {
    NONE,
    WINDOW_OPENED,
    SUCCESS,
    FAILURE
}

interface ManualOAuth2FlowState {
    authStatus: AuthStatus;
}

/**
 * A React component to handle OAuth 2.0 authentication flow manually.
 * This is not a common or ideal way to handle OAuth 2.0 authentication flow in real-world applications.
 * In some authorization providers there's an issue with dynamic callback URLs.
 * Since notebooks can be started using random URL we cannot speicfy fixed callback URL.
 *
 * This component provides an interactive method for users to authenticate
 * through an external OAuth provider.
 *
 * Workflow:
 * 1. An authentication window is opened for the user upon invoking `openAuthWindow`.
 *    - This makes a request to the 'login' endpoint with the origin specified.
 *    - The server responds with a redirect URL, which is then opened in a new window.
 *
 * 2. After the user completes the authentication on the OAuth provider's site,
 *    they are redirected back, with an authorization code in the URL.
 *
 * 3. Users are instructed to copy and paste this URL into an input field manualy
 *
 * 4. This code is then sent to the 'login' endpoint to exchange it for tokens or finalize the authentication process.
 *
 * 5. The component's state is updated based on the success or failure of the authentication.
 *
 */
export default class ManualOAuth2Flow extends Component<{}, ManualOAuth2FlowState>  {
    private authWindow: Window | null = null;

    constructor(props: {}) {
        super(props);
        this.state = {
            authStatus: AuthStatus.NONE
        };
    }


    openAuthWindow = async () => {
        try {
            const redirect_url = await requestAPI<any>(
                'login',
                {
                    method: 'GET'
                }
            );
            console.debug("Authorization redirect URL is" + redirect_url);

            this.authWindow = window.open(redirect_url, 'authWindow', 'width=600,height=400');
            this.setState({authStatus: AuthStatus.WINDOW_OPENED});
        } catch(error) {
            console.error("Error during start of authentication:", error);
            this.setState({ authStatus: AuthStatus.FAILURE });
        }

    }

    closeAuthWindow = () => {
        if (this.authWindow && !this.authWindow.closed) {
            this.authWindow.close();
        }
    }

    handleURLInput = async (e: { target: { value: any; }; }) => {
        const redirectURI = e.target.value;
        const code = new URL(redirectURI).searchParams.get('code');
        if (code) {
            try {
                await requestAPI<any>(
                    'login?code=' + code,
                    {
                        method: 'GET'
                    }
                );
                this.closeAuthWindow();
                this.setState({ authStatus: AuthStatus.SUCCESS });
            } catch (error) {
                this.closeAuthWindow();
                console.error("Error during authentication:", error);
                this.setState({ authStatus: AuthStatus.FAILURE });
            }
        }
    }

    render() {
        return (
            <div className={LOGIN2_DIALOG_CLASS}>
                {this.state.authStatus === AuthStatus.NONE &&
                    <div>
                        <p>Authenticate process will start. After you clik a new window will be opened.</p>
                        <ul>
                            <li>Please <b>wait</b> for the authentication window to redirect you back to 127.0.0.1.</li>
                            <li><b>Ignore</b> the failed connection error message.</li>
                            <li>And then <b>copy and paste</b> the full URL you are redirected to.</li>
                        </ul>

                        <button className={LOGIN2_BUTTON_CLASS} onClick={this.openAuthWindow}>Click here to start.</button>
                    </div>
                }
                {this.state.authStatus === AuthStatus.WINDOW_OPENED &&
                    <div>
                        <p>A new authentication window has been opened.</p>
                        <ul>
                            <li>Please <b>wait</b> for the authentication window to redirect you back to 127.0.0.1.</li>
                            <li><b>Ignore</b> the failed connection error message.</li>
                            <li>And then <b>copy and paste</b> the full URL you are redirected to in here:</li>
                        </ul>
                        <input type="text" className={LOGIN2_INPUT_CLASS} onChange={this.handleURLInput} />
                    </div>
                }
                {this.state.authStatus === AuthStatus.SUCCESS &&
                    <div>
                        <p>Authentication successful!</p>
                    </div>
                }
                {this.state.authStatus === AuthStatus.FAILURE &&
                    <div>
                        <p>Authentication failed!</p>
                    </div>
                }
            </div>
        );
    }
}


export async function showLogin2Dialog() {
    await showDialog({
        title: LOGIN_BUTTON_LABEL,
        body: (
            <ManualOAuth2Flow></ManualOAuth2Flow>
        ),
        buttons: [Dialog.cancelButton({label: "Close"})],
        hasClose: false
    });
}
