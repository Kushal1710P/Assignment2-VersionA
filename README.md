# Setup

This will download Assignment 2 locally, allowing you to work on your scripts and upload (push) them back up to GitHub.

1. Use the green **Code** button to copy the SSH link into your clipboard.
1. Clone your assignment repository into your ~/ops445/assignment2 directory.

```bash
git clone <ssh link> ~/ops445/assignment2/
```

# Submission

1. Run the testing script. You can use this script to run the tests as stated in the Assignment 2 wiki page.  
Please note that this test run script does not check your script docstring or your function docstring.  

```bash
cd ~/ops445/assignment2/
pwd #confirm that you are in the right directory
python3 ./checkA2.py
```

2. Commit and push (upload) your assignment work. **Give your commit a sensible message**:

```bash
git add assignment2.py
git commit -m "Individual message or note."
git push
```

3. Once you have pushed to Github, you must also submit your *assignment2.py* to Blackboard. 

You can make changes to your scripts and reupload as many times as you like. Make sure you commit+push to do so.

**Note:** Your assignment is automatically submitted at the due date and time using the last published code. Any changes you publish after the due date won't be marked or seen by your professor.

