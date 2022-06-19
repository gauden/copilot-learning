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

## Version 01

Again a short excursion, this time into refactoring the code produced in yesterday. The actions taken:

1. The code was segmented into functions. All it required was the creation of descriptive function names, Github suggested docstrings which were accepted, and in one case tweaked to make it more explicit (see docstring for `loop_through_all_publications_and_collect_ids()`).
2. The query string function suggested by Copilot repeatedly malfunctioned. I collected a template from Pubmed and also reminded Copilot via a comment to url-encode the string before using it to fetch data.

As a result, the refactored code is very close to working, but still crashes with an error. The logic in `loop_through_all_publications_and_collect_ids()` is faulty. Not sure it is programming error (faulty logic from Copilot) or whether I need to teach it how to seed the `retmax` and `retstart` variables to guide through downloading successive pages of paper IDs.

On the agenda for the quick experiment tomorrow: get the download loop working, and for extra marks, start the process of storing all records in a local SQLite table rather than a plain text file.

## Version 02

The challenge is morphing with every day that passes. I find that I am trying to replicate with Copilot and the standard library a routine that is easily done in Biopython (see the [tutorial](http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec168) section 9.16.2). 

Today I spent 52 minutes refactoring the code and trying to follow the correct sequence of steps, including:

1. Setting global values for `EMAIL` and `TOOL` to keep the Entrez system informed, as they request. Ensuring that these values are used throughout the functions.
2. Using the `esearch` tool to set up a web environment and to retrieve Ids and a count of records.
3. Dividing the records into batches of Ids, retrieving each batch of records, and storing them in the output file.

Most of the hour spent on this involved micro-managing Copilot into separating the code between `esearch` and `efetch`. Once the two functions were divided up, with good function names, then Copilot appeared to know the logic of each and certainly took care of all the conversion back and forth between strings and XML formats.

There was one instance where StackOverflow was needed: despite trying multiple types of comment, I could not get Copilot to convert ElementTree elements to strings. I finally had to add the `method="xml"` parameter by hand in line 143:

```python
f.write(ET.tostring(record, encoding="unicode", method="xml"))
```
Most importantly, after three sessions with Copilot on this challenge, I managed to get a retrieval of a dataset. The particular search I gave it retrieved 83 records, but the final output file contained only 20. It appears the batch retrieval process is not working. A challenge for tomorrow?

## Version 03

Thirty three minutes to complete today's experiment. 

1. Copilot made an error in using the `esummary` tool when `efetch` was needed -- that took some debugging when the script started failing again and a manual correction.
2. Also, having retrieved all records, each as an `ElementTree.ET` object, in a list, I wanted to bring all the records into one complete XML object. I could not find a comment to get Copilot to do that. I had to give a highly specific comment to guide it: `# create root XML element called "PubmedArticleSet" and add records to it` (see line 152 of today's commit.)

The key lessons from this day:

- Copilot cannot be expected to know the arcana of specific packages and tools e.g. the Pubmed search tools and the `xml` module in the Python standard library. I would have expected difficulty with the first, but I would not have expected any issues with the standard library. Indeed, it had been my hope that I could use Copilot to explore the standard library at least.
- Having said that, in just over two and a half hours total, Copilot has given me a tool that would have taken me much longer to write were I to delve through the manuals and documentation of a ton of packages. Indeed, I think the total number of such lookups over the past three days was once or twice a day on average.

At the end of this exercise, I have the extractor working, giving me an XML file on my hard disk with all the references returned from a Pubmed search. Where to next? SQLite? Let's see tomorrow.

## Version 04

One of the recurring problems with SQL is the tedium of creating tables and fields that correspond with the data structure. Today's experiment started with the idea: can I avoid that tedium by parsing an XML object, creating tables in SQLite that correspond to the fields and attributes of that object, including preserving relations, and then parse my search results, inserting them into the database.

The answer: I am being too ambitious. Today's exercise took 54 minutes, including the writing of this note, and despite multiple efforts to prompt recursive analysis of the XML object, I could not get a mapping to the SQL format I needed, even when I tried to convert to JSON as an intermediate format.

Maybe I am being too ambitious? Let's see tomorrow.

Total time: 54 minutes

## Version 05

Another attempt to simplify the problem. Create two data classes that represent an author and a paper. Create another data class that represents a link between a specific author and a specific paper. Use these as the basis for creating the two tables (author and paper) and the relation between them (one author can write multiple papers and one paper can have multiple authors).

First commit in this version: almost 400 lines of Copilot generated code, creating the tables, creating access methods. Too detailed. No agreement in record structure between functions, still needs immense level of pruning and rewriting. At this stage would take as much to correct this as it would to write it myself. Let's start afresh. [Commit message: Try detailed record creation for author and paper.]

Second commit: Guided Copilot to create a simple `Author` dataclass with just name and affiliation for each author. Included extensive XML snippets in the comments to guide Copilot specifically on where to look for the information. Only now is this working, collecting every author from all papers in the search. [Commit message: Collect simple record for each author in search.] 

Total time: 80 minutes

## Version 06

Starting this iteration with the plan to extract the paper details from the XML object in the same way as I did with the `Author` class, by providing a shorn down model of the fields I am interested in into the docstring of the functions. Using this method, it was possible to get all the boilerplate done for the extraction of fields from the XML element, and the creation of the dataclass in under five minutes. This is such a tedious task usually that it just stops me going any further. Copilot excels at this. It indeed feels like a junior assistant simply tasked with building up repetitive lines of code and trustworthy enough to do it well. What it does not do, is mentally parse the XML and correctly traverse the tree from root to the desired branch. This has to be done manually for every term, just to make sure everything is consistent.

The whole of the time spent on this experiment today was to check every field I wanted to collect into the dataclass, ensure that it was correctly located in the tree traversal, remind Copilot repeatedly to check for `AttributeError` and to account for it correctly, and in keeping the dataclasses in sync with the fields I was collecting.

At the end, this module has delivers what it says on the lid (though it has strayed heavily from the original mission as described in the module docstring -- "all comments are lies"):

1. It globs through all the XML files in the data directory
2. It parses all the `PubMedCitation` elements in each of the files
3. It yields a `record` dataclass for each citation.

Four test files have been created in the data directory and the parsing is working well for each. Where to go next? Write some tests? Get back to the SQL side? Let's see what tomorrow feels like.

[Commit message: Parse all papers in data directory.]

Total time: 175 minutes

## Version 07

There are four outstanding challenges for this set of scripts to become a useable package, if this is to make it as my first release on PyPI. 

1. Create a database backend using the `sqlite3` package. Because no target user is going to exceed SQLite's capabilities. Because SQLite is in the standard library. Because I have not done this before, so Copilot will help me on another learning path.
2. Reorganize the suite of scripts into an installable package.
3. Set up a set of tests 
4. Provide the necessary documentation and release.

At this stage, today's experiment will focus on the first challenge. We create a branch, `sql_setup`, and dive in.

In the first session of coding, all the basic functions were rapidly set up, in about 25 minutes, but this was followed by a lengthy session, still unfinished, of understanding why I am getting a `sqlite3.OperationalError: unable to open database file`. Debugging at this stage:

- the SQL code generated by Copilot turned out to be almost correct. I was able to get it to work on the command line to create the database and the tables _after I removed the trailing comma from the field definitions_. Somehow I had expected Copilot to take care of that.
- I manually created the test database using the DB Browser for SQLite app and gave it read-write access for all users. This still did not work.

Embarrassed to report: No sooner did I write the above than I discovered that I was in the wrong working directory and got my pathnames messed up. Copilot is not a cure for stupidity.

[Commit message: V07.01 initial commit of SQLite feature]

Total time: 89 minutes
