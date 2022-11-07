# Sonarqube Reports

## About The Project

The community version does not have an interface to download reports. Using this script, the issues can be downloaded in CSV format. 

## Getting started

### Prerequisites

* Python3

### Installation

1. Clone the repository

   ```sh
   cd /Data
   git clone https://github.com/govindasamyarun/sonarqube-reports.git
   ```
   
2. Execute the script using -h option 

   ```sh
   pwd: /Data/sonarqube-reports
   python3 sonarqube.py -h
   ```
   It outputs the mandatory options required to execute the script
   
## Options

   * -H or --hostname 
   * -U or --username 
   * -P or --password 
   * -O or --output-dir
   * -T or --type (optional) 
      * Accepted values are BUB, CODE_SMELL, VULNERABILITY, ALL
      * If the type is none, the default type is set to ALL 

## Examples

1. python3 sonarqube.py -H sonarqube.abc.com -U testuser -P testpassword -O /Users/arun/Downloads/sonarqube/reports -T bug 

   * Output file
      * /Users/arun/Downloads/sonarqube/reports/bug.csv
   
2. python3 sonarqube.py -H sonarqube.abc.com -U testuser -P testpassword -O /Users/arun/Downloads/sonarqube/reports 

   * Output files
      * /Users/arun/Downloads/sonarqube/reports/bug.csv
      * /Users/arun/Downloads/sonarqube/reports/code_smell.csv
      * /Users/arun/Downloads/sonarqube/reports/vulnerability.csv

## Support

Use the issues tab to report any problems or issues.

## License

Distributed under the MIT License. See LICENSE for more information.

## Contact

* [LinkedIn](https://www.linkedin.com/in/arungovindasamy/)
* [Twitter](https://twitter.com/ArunGovindasamy)