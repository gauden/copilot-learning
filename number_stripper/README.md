# Problem

I found a table of teas and optimal temperatures on [artfultea.com](https://www.artfultea.com/tea-wisdom-1/tea-brewing-temperature-guide) and I wanted to quickly extract a table of teas and the appropriate water temperature. The only issue was that the temperatures were in Fahrenheit and my devices work in Celsius.

The easy way to do it, of course, is to just convert the numbers on my calculator, but this type of problem recurs often enough that I want to see if I can write a script fast enough to:

1. Establish the boiler-plate code (see what I did there?) that I would need to write every time I wrote a script like this and get that out of the way. E.g. Load the text from a file, display a list of lists as a Markdown table, etc
2. Write the processing functions specific to the text I am looking at, e.g. extract the numbers of every line and convert them to Celsius.
3. Pass the processing function to a main loop so that a final form would be a command line app where the text file and the processing function could be passed in as arguments.

# Solution and Reflections

1. The [script](./main.py) was written in around fifteen minutes (I should time myself next time). I accepted everything Copilot suggested, writing only the comments, docstrings, and minor edits on accepted blocks of code. Only once did I need to find alternate versions of suggested code blocks (this was in the transpose function).
2. Another difference: I use much more longer function names than I would normally do when hand-coding. I found that this style generated better code suggestions.
3. The solution is heavily coupled to the structure of the input data, with no level of abstraction but that was because I was following the process I would have used if I had hand-coded it myself.
4. I ended up straying from the docstring at the top of the script. I just returned a dictionary with a string for both key and value when the docstring implied a `Dict[str, List[int]]`. That was my choice as I inserted the types in the function signature.
5. No tests. That was my own choice. I would usually do this for a quick and dirty solution. I am trying to see if I could code such rapid solutions to be using them more frequently, just because Copilot lets me.
6. Not a command-line app, yet, maybe tomorrow. I want to keep this real and brief.

Would I have done anything different if I was coding by actual typing rather than pressing the tab key? I would probably have not written lines 43 to 51 like this:

```python
    # suggestion from Copilot
    headers = []
    values = []
    for line in lines:
        if ":" in line:
            header, value = line.split(": ")
            headers.append(header)
            values.append(value)
    values = [convert_to_celsius(v) for v in values]
    table = dict(zip(headers, values))
```
I would have done this:

```python
    # my version
    table = dict()
    for line in lines:
        if ":" in line:
            header, value = line.split(": ")
            value = convert_to_celsius(value)
            table[header] = value
```

It would have been more succinct and would have avoided the need to transpose the table in the `convert_to_markdown` function. Having said that, when transposition is needed, it would usually have consumed a lot more time than it took to press tab. Also, the function to produce the Markdown table is neater than anything I would have done and still very readable.
