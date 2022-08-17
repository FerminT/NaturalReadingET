# Eye-tracking during natural reading - Long Texts
## Definitions
A *word* is defined as a sequence of characters between two blank spaces, with the exception of those characters that correspond to punctuation signs.
 - *Unfrequent word*: its number of appearences in the latinamerican subtitles database from [EsPal](https://www.bcbl.eu/databases/espal/) is less or equal to 100.
 - *Short sentence*: less or equal to 5 words.
 - *Long sentence*: greater or equal to 30 words.
 - *Long word*: greater or equal to 10 chars.
 - *Unfrequent characters*: ¿; ?; ¡; !; “; ”; —; «; (; ).

## Corpus
The corpus is composed of 17 short stories (*items*), all written in Spanish as spoken in Buenos Aires. Most of them (14) were extracted from “100 covers de cuentos clásicos”, by Hernán Casciari. The original stories were written by several different authors and were subsequently simplified, translated (if needed) and re-written in Spanish by Casciari. This way, there is diversity in literary style, while maintaining both difficulty and slang constant.

On average, these are 750 (+/- 47) words long (min: 676; max: 844) and take 3 minutes to read (51 minutes total).
### Selection criteria
- Minimize dialogue.
- Minimize short and long sentences.
- Minimize unfrequent words and characters.
- Self-contained.
- No written dates.
- Not shorter than four hundred words.
- Not longer than two thousand words.

There is a correlation between *minimizing dialogues* and *minimizing unfrequent characters*, as dialogues are usually characterized by such.
## Methodology
* Stimuli creation (see config.mat:
    * Resolution: 1080x1920.
    * Font: Courier New; Size: 24; Color: black; Background color: grey.
    * Linespacing: 55px.
    * Max lines per screen: 14.
    * Max chars per line: 99.
    * Left margin: 280px.
    * Top margin: 185px.
* The participant is told that, after reading each text, he/she will be evaluated with three comprehensive questions.
* Their reading skills are also inquired?
* Item order is random.
* Once an item has been read, comprehension questions are answered.
* The following item is displayed by pressing a button.
* Each item is a *block*. After each block, a one minute break and eye-tracker calibration follows.
* After the 30 minute mark, a longer break takes place.
