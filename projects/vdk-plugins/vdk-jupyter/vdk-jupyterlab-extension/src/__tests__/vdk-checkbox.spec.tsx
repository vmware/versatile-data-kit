import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { VDKCheckbox } from '../components/VdkCheckbox';

describe('VDKCheckbox Component', () => {

    it('renders without crashing', () => {
      const component = render(<VDKCheckbox checked={false} onChange={jest.fn()} label="Test" id="test" />);
      const checkbox = component.getByLabelText('Test');
      expect(checkbox).toBeDefined();
    });

    it('initial checked state is set correctly', () => {
      const component = render(<VDKCheckbox checked={true} onChange={jest.fn()} label="Test" id="test" />);
      const checkbox = component.getByLabelText('Test') as HTMLInputElement;
      expect(checkbox.checked).toBe(true);
    });

    it('onChange is called when the checkbox is clicked', () => {
      const mockOnChange = jest.fn();
      const component = render(<VDKCheckbox checked={false} onChange={mockOnChange} label="Test" id="test" />);
      const checkbox = component.getByLabelText('Test');

      fireEvent.click(checkbox);
      expect(mockOnChange).toHaveBeenCalledWith(true);
    });

  });
