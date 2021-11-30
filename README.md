# CSS-lab-christmas-2021
Christmas paper of the CSS lab 2021

## Languages and emojis
We look into the following languages:
* ar (arabic)
* en (english)
* fr (french)
* de (german)
* hi (hindi)
* it (italian)
* es (spanish)
* pt (portugues)
* ja (japanese)
* ru (russian)
* id (indonesian)
* tr (turkish)
* ko (korean)
* th (thai)

And the following emojis:
* 'wavinghand':"👋",
* 'raisedhand':"✋",
* 'raisedbackhand':"🤚",
* 'vulcansalute':"🖖",
* 'okhand':"👌",
* 'pinchedfingers':"🤌",
* 'pinchinghand':"🤏",
* 'victoryhand':"✌️",
* 'crossedfingers':"🤞",
* 'loveyougesture':"🤟",
* 'signofthehorns':"🤘",
* 'callmehand':"🤙",
* 'backhandindexpointingleft':"👈",
* 'backhandindexpointingright':"👉",
* 'backhandindexpointingup':"👆",
* 'middlefinger':"🖕",
* 'backhandindexpointingdown':"👇",
* 'indexpointingup':"☝️",
* 'thumbsup':"👍",
* 'thumbsdown':"👎",
* 'raisedfist':"✊",
* 'oncomingfist':"👊",
* 'leftfacingfist':"🤛",
* 'rightfacingfist':"🤜",
* 'clappinghands':"👏",
* 'raisinghands':"🙌",
* 'openhands':"👐",
* 'palmsuptogether':"🤲",
* 'handshake':"🤝",
* 'foldedhands':"🙏"

## Data
The data is stored on medea at `data/CSS-lab-christmas-2021`. The directory includes the following sub-directories:
* `counts` contains the ocurrences for all 30 hand-emoji available on twitter for 14 languages between 2019-01-01 and 2021-11-28, as well as a "baseline" count (i.e. the number of tweets in that language for a given day).
* `tweets` contains the tweets that include a "🤌" (pinched fingers) emoji for all 14 languages between 2019-01-01 and 2021-11-28 (excluding retweets).
* `sentiment` contains the sentiment of the tweets in the `tweets` directory, characterized with an [xlm-roberta model](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment) fine-tuned for sentimend characterisation.

**NOTE:** The results for `tweets` and `sentiment` for english are still coming in.

## Downloading the data
You can download the data by running the following command in your terminal:  
 `rsync -avze ssh USERNAME@medea:/data/CSS-lab-christmas-2021/ data/`
 
This assumes that you are in a directory that includes an empty folder called "data", in which the data will be copied. Replace USERNAME with your username on medea.
If you don't have `rsync` installed, you can install it by running  

`sudo apt install rsync grsync`

## Code
The code needs Twitter API credentials and a language model to run, which are not included in the repository.
