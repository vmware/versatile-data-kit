import {render, fireEvent, waitFor, cleanup} from '@testing-library/react';
import { requestAPI } from '../handler';
import ManualOAuth2Flow from "../components/Login2";
import React from "react";

jest.mock('../handler', () => ({
    requestAPI: jest.fn()
}));


describe('ManualOAuth2Flow Component', () => {

    beforeEach(() => {
        window.open = jest.fn();
    })

    afterEach(() => {
        jest.clearAllMocks();
        cleanup()
    });

    it('should render without crashing', () => {
        render(<ManualOAuth2Flow/>);
    });

    it('should open a new authentication window on button click', async () => {
        (requestAPI as jest.MockedFunction<typeof requestAPI>).mockResolvedValue('http://auth-url.com');
        const component = render(<ManualOAuth2Flow/>);
        const button = component.getByText("Click here to start.");
        fireEvent.click(button);

        await waitFor(() => {
            expect(requestAPI).toHaveBeenCalledWith('login', { method: 'GET' });
        });
    });

    it('should prompt for URL input after opening the auth window', async () => {
        (requestAPI as jest.MockedFunction<typeof requestAPI>).mockResolvedValue('http://auth-url.com');
        const component = render(<ManualOAuth2Flow/>);
        const button = component.getByText("Click here to start.");
        fireEvent.click(button);

        await waitFor(() => {
            // console.log(prettyDOM(component.container))
            const input = component.container.querySelector('input')
            expect(input?.textContent).toBe("")
        });
    });

    it('should display success message after successful authentication', async () => {
        (requestAPI as jest.MockedFunction<typeof requestAPI>)
            .mockResolvedValueOnce('http://auth-url.com')
            .mockResolvedValueOnce({ success: true });

        const component = render(<ManualOAuth2Flow/>);
        const button = component.getByText("Click here to start.");
        fireEvent.click(button);

        await waitFor(() => {
            const input = component.getByRole('textbox')
            fireEvent.change(input, { target: { value: 'http://127.0.0.1?code=valid_code' } });
        })

        await waitFor(() => {
            expect(component.getByText("Authentication successful!")).toBeTruthy();
        });
    });



    it('should display failure message after failed authentication', async () => {
        (requestAPI as jest.MockedFunction<typeof requestAPI>)
            .mockResolvedValueOnce('http://auth-url.com')
            .mockRejectedValueOnce(new Error('Authentication error'));

        const component = render(<ManualOAuth2Flow/>);
        const button = component.getByText("Click here to start.");
        fireEvent.click(button);

        await waitFor(() => {
            const input = component.getByRole('textbox')
            fireEvent.change(input, { target: { value: 'http://127.0.0.1?code=invalid_code' } });
        })

        await waitFor(() => {
            expect(component.getByText("Authentication failed!")).toBeTruthy();
        });
    });

});
