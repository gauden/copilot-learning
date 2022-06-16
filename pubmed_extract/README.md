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