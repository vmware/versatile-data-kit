This is a POC level implementation of a plugin which changes the logging format of vdk-core to LTSV for the purposes of structured data visualization.

The new format has the following fields, separated by tabs:
 * timestamp: a timestamp of when the log is made;
 * created: the same timestamp in the unix epoch format;
 * jobname: the name of the data job;
 * level: the logging level - one of INFO, WARNING, DEBUG, ERROR;
 * modulename: the name of the module, inside of which the logging call is made;
 * filename: the name of the file containing the logging call being made;
 * lineno: the number of the line of code, at which the logging call is made;
 * funcname: the name of the function, inside which the loggin call is made;
 * attemptid: string identifying this particular execution of the data job;
 * message: any additional logged information.

The label names follow the labelling recommendations found at http://ltsv.org/.
