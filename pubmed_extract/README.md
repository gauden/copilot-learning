# Problem

As a basic exercise in bibliometric analysis, let us try and create a command-line app that takes in an author name, start year, and end year as parameters, downloads records of that author's papers from Pubmed, and counts the number of papers annually.

# Solution

## Version 00

Within the time allotted for this daily experiment, Copilot offered a credible code block that could serve as a credible starter. It has many strengths and weaknesses.

### Strengths

1. It sets up a frame for a working command line application using only the standard library. It includes the prompts, help messages, sets the logging level with a `--verbose` flag, and validates the types of parameters correctly.
2. It sets up a correct sequence of calls to the `efetch` interface of Pubmed, creating the query string, retrieving the UIDs of the papers, storing that locally, and using it to collect the full records.
3. If it did manage to retrieve the records, it does process them correctly and creates a data structure amenable to presentation in the form of a Markdown table.

### Weaknesses

For the next experiment, a few of the shortcomings must be improved, consider these a list of TODOs:

1. The query string is not formatted correctly -- this may be something the user needs to correct by hand. Because of this, of course, the search does not retrieve anything.
2. The code is not divided into functions. It is not clear whether one can expect Copilot to do this on its own. It may need to be prompted by hand and then debugging would be easier.
3. The code is not very well behaved. It does not provide Pubmed with a contact email as requested by the terms of use. 
4. There is a superfluous import of the `time` standard module; easily corrected by hand, but let's leave that till later as there may be uses for it in the final version.

Try this again tomorrow, guiding it with proper functional structure, adding the query string by hand, and prompting Copilot to retrieve an email stored as an environmental variable and to use that in its interaction with `efetch`.