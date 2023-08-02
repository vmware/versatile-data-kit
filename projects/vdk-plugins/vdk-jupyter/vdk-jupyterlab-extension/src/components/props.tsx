export type IJobPathProp = {
  /**
   * Current Job path or the path to job's parent directory
   */
  jobPath: string;
};

export type IJobNameAndTeamProps = {
  /**
   * Current Job name
   */
  jobName: string;
  /**
   * Current Team name
   */
  jobTeam: string;
};

export type IJobFullProps = IJobPathProp & IJobNameAndTeamProps;

export interface JupyterCellProps {
  /**
   * Source code of the cell
   */
  source: string;
  /**
   * Type of the cell
   */
  type: string;
}
