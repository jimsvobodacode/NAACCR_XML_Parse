<p align="center">

  <h2 align="center">NAACCR XML Parser</h3>

  <p align="center">

  </p>
</p>


<!-- ABOUT THE PROJECT -->
## About The Project


The NAACCR XML Parser will parse NAACCR data files in the v21 XML data format.  The parsed data is stored in a local sqlite3 database and is also saved as a tab delimited text file.


### Built With

* Python 3.9.X
* Uses packages sqlite3, pandas (for file export)
* Visual Studio Code


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.  Process has been tested on Windows 10.

### Prerequisites

If not done already, download and install the current version of Python from [python.org](https://www.python.org/).

You may also want to install [DB Browser](https://sqlitebrowser.org/) to view the data in the sqlite3 database.


### Installation

1. Clone the repo
   ```
   git clone https://github.com/jimsvobodacode/NAACCR_XML_Parse.git
   ```
2. Install pip packages
   ```
   pip install pandas
   ```


<!-- USAGE EXAMPLES -->
## Usage

1. Copy your NAACCR files to the "data" subdirectory
2. Open Powershell in Windows 10
3. Navigate to your project directory
4. Run ```python app.py```


<!-- CONTRIBUTING -->
## Contributing

I'm only accepting bug fixes at this time.




<!-- CONTACT -->
## Contact

Jim Svoboda - jim.svoboda@unmc.edu - email
