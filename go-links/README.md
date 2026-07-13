# Go links

Google has a functionality known as go-links that allow you to shorthand URLs. This is my implementation of this tooling. 


You can add entries by appending to the entries array like this:
```json
{
    "entries": [
        {
            "go-link": "yt",
            "target-link": "https://www.youtube.com/"
        }
    ]
}
```
Then target it via (example) `localhost:3000/yt`.