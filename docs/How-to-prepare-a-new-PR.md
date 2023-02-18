The page contains some recommendation to follow when preparing a new change (PR) 


### Self-evaluate Change/Feature Proposal

Before suggesting a change/feature, think if this change only serves your needs, or it is broader, that is good for the project itself because it serves multiple users. If it is a very specific change limited in its usefulness, can it be generalised to meet the needs of more users? If yes, propose the more broadly useful feature.
Reach out to us and the community - through slack, mail to discuss your idea. We are happy to help.

### Submit Design (if needed)

For more complex features/changes, submitting your design is valuable, if possible,  before you even write a single line of code. This may involve choice of data structures, configuration parameters, other support services, scalability considerations and its interface. It is vastly more efficient and easier to discuss a design and  address concerns at this stage than change an implementation. If you are aware of possible alternative solutions to the problem, describe why you think your solution approach is the best.
That said, in some cases one may actually need to do some prototyping  to even suggest a viable design, one that meets requirements. We can discuss together what is appropriate for this case.

### Tackle non-functional or refactoring changes first

Before you get started on your new feature determine whether there are some clean-up tasks. This could be removing whitespace, renaming some variables or methods, adding more error handling, or re-organising your code such as moving a file, or code refactoring.. Address these first as a separate commit ensuring that it causes no breaks. In so doing you have addressed non-functional changes and kept your feature related commit history separate.

### Break your code commits into  small self-contained units

Smaller changes are easier to review, test, and approve. Your reviewer will be grateful! Reviewing larger commits is daunting and tend to be postponed!  Small changes are also easier to merge safely, root-cause in case of issues, and rollback if necessary. A function/feature may be comprised of one or more atomic commits.

Note that we are less concerned about the number of files touched in a commit than with the fact that it deals with a single aspect and does not break anything. For instance if you seek to introduce an additional parameter in a bunch of function calls, the first add the additional parameter in all the affected files. Commit this change before even attempting to use the additional parameter in the function implementation. Once that is complete, feel free to submit a second commit.

In the context of bug fixes, do not combine two or more bug fixes in a single commit, keep them instead separate and have each commit message point back to the issue it is  fixing.

Features and or bug fixes that pertain to different data base solutions, or cloud providers or input/output formats should be kept separate. This eases the task of back porting fixes to deployments that rely on the solution.

Below is yet another example, to help reinforce the philosophy  of breaking up a feature implementation into smaller sub-tasks, that might themselves map to multiple atomic commits.
It's recommended to start with changes in user-facing interfaces necessary - make sure the API - REST, methods and their documentation is reviewed first before their implementation.

1. Update environment for you change - for example update build system to support your change
2. Update API by adding the new methods, fields, etc. related to your change and their documentation (javadoc, openapi defintions, etc.)
3. Introduce the change implementation in backend service
4. Introduce change implementation in the relevant Command Line Interface (CLI) / config for the change;
5. Update the user documentation.

This is just an example. For some changes, it may make sense to do them together in a single PR. Just make sure to keep to the "spirit of the rules" - let's make changes that are easy to review, test, merge, troubleshoot, rollback. 

### Write a good commit message

Commit messages are invaluable in understanding the project and down the road are invaluable in troubleshooting problems. Your message should contain the what and why of the change. While the reviewer will evaluate if you have achieved what you say you seek to achieve,   providing  the Why eliminates guessing on the part of the reviewer on why the patch even exists. Further  in the commit message should include test results  and itemise any and all tests that were not performed. The latter often stems from a  lack of some special purpose hardware or inability to access some cloud instance.

The template for all commit messages is described in [git-commit-template.txt](https://github.com/vmware/versatile-data-kit/blob/main/support/git-commit-template.txt)

### Address Reviews Thoughtfully.

The project runs automated pre-merge tests on each change. They need to pass first.

Once you are past the automated tests, other contributors to the project, including the maintainer will review your changes. It is imperative that you review these comments carefully, implementing those that you concur with, and for those that you disagree with explaining why, sharing your reasons versus dismissing or ignoring them. If in doubt, ask questions on the project  platform , for example the git comments, slack, mail.  This process of reviewing and addressing comments may take several iterations.

Do not take any comments/criticisms personally and when you are a reviewer provide constructive comments.

