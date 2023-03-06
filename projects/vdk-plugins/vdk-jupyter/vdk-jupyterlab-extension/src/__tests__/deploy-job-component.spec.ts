import DeployJobDialog, { IDeployJobDialogProps } from "../components/DeployJob";
import { render, fireEvent } from '@testing-library/react';
import { jobData } from "../jobData";
import { VdkOption } from '../vdkOptions/vdk_options';

const defaultProps: IDeployJobDialogProps= {
    jobName: "test-name",
    jobTeam: "test-team",
    jobPath: "test-path",
    vdkVersion: "test-version"
};

describe('#constructor()', () => {
    it('should return a new instance', () => {
      const box = new DeployJobDialog(defaultProps);
      expect(box).toBeInstanceOf(DeployJobDialog);
    });
});

describe('#render()', () => {
    it('should return contain job name input with placeholder equal to jobName from props', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobName);
        expect(input).toBe(component.getAllByLabelText("Job Name:")[0])
    });

    it('should return contain job team input with placeholder equal to jobTeam from props', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobTeam);
        expect(input).toBe(component.getAllByLabelText("Job Team:")[0])
    });

    it('should return contain job path input with placeholder equal to jobPath from props', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobPath);
        expect(input).toBe(component.getAllByLabelText("Job Path:")[0])
    });

    it('should return contain vdk version input with placeholder equal to vdkVersion from props', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.vdkVersion);
        expect(input).toBe(component.getAllByLabelText("VDK version:")[0])
    });
});

describe('#onEnableClick', () => {
    it('should put a flag for enabled in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const enableCheckbox = component.getAllByLabelText("Enable")[0] as HTMLInputElement;
        expect(enableCheckbox.checked).toEqual(false);
        fireEvent.click(enableCheckbox);
        expect(enableCheckbox.checked).toEqual(true);
        expect(jobData.get(VdkOption.DEPLOY_ENABLE)).toEqual("1");
        expect(jobData.get(VdkOption.DEPLOY_DISABLE)).toEqual("");
    });
});

describe('#onDisableClick', () => {
    it('should put a flag for disabled in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const disableCheckbox = component.getAllByLabelText("Disable")[0] as HTMLInputElement;
        expect(disableCheckbox.checked).toEqual(false);
        fireEvent.click(disableCheckbox);
        expect(disableCheckbox.checked).toEqual(true);
        expect(jobData.get(VdkOption.DEPLOY_DISABLE)).toEqual("1");
        expect(jobData.get(VdkOption.DEPLOY_ENABLE)).toEqual("");
    });
});

describe('#onNameChange', () => {
    it('should change the job name in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobName);
        fireEvent.change(input, {target: {value: 'second-name'}})
        expect(jobData.get(VdkOption.NAME)).toEqual('second-name');
    });
});

describe('#onTeamChange', () => {
    it('should change the job team in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobTeam);
        fireEvent.change(input, {target: {value: 'second-team'}})
        expect(jobData.get(VdkOption.TEAM)).toEqual('second-team');
    });
});

describe('#onRestApiUrlChange', () => {
    it('should change the rest api url in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText("rest-api-url");
        fireEvent.change(input, {target: {value: 'random-url'}})
        expect(jobData.get(VdkOption.REST_API_URL)).toEqual('random-url');
    });
});

describe('#onPathChange', () => {
    it('should change the path in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.jobPath);
        fireEvent.change(input, {target: {value: 'other/path'}})
        expect(jobData.get(VdkOption.PATH)).toEqual('other/path');
    });
});

describe('#onVdkVersionChange', () => {
    it('should change the vdk version in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText(defaultProps.vdkVersion);
        fireEvent.change(input, {target: {value: '0.10'}})
        expect(jobData.get(VdkOption.VDK_VERSION)).toEqual('0.10');
    });
});

describe('#onDeploymentReasonChange', () => {
    it('should change the vdk version in jobData', () => {
        const box = new DeployJobDialog(defaultProps);
        const component = render(box.render());
        const input = component.getByPlaceholderText('reason');
        fireEvent.change(input, {target: {value: 'Another reason'}})
        expect(jobData.get(VdkOption.DEPLOYMENT_REASON)).toEqual('Another reason');
    });
});