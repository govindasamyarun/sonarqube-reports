import os, requests, csv, sys, argparse

class sonarQube():
    def __init__(self, hostname, username, password, output_dir, reports):
        # Initialize variables 
        self.auth_url = 'https://{}/api/user_tokens/search'.format(hostname)
        self.projects_url = 'https://{}/api/components/search_projects'.format(hostname)
        self.issues_url = 'https://{}/api/issues/search'.format(hostname)
        self.username = username
        self.password = password
        self.pageSize = 500 # Controls the number of results returned, it is set to max value 

        # Project variables 
        self.projects = []
        self.isProjectsLastPage = False # pagination
        self.projectsPage = 1 # pagination 

        # Issues variables
        self.issues = []
        self.isIssuesLastPage = False # pagination
        self.issuesPage = 1 # pagination
        self.outputFilePath = output_dir.rstrip('/') # Remove the slash at the end 

        # Reports varaiable 
        self.reports = reports

    def authenticate(self):
        # This function is used for authentication
        # If authentication fails it exits the program 
        response = requests.get(self.auth_url, auth=(self.username, self.password))
        try:
            response.json()
        except Exception as e:
            print("{'success': False, 'status_code': {}, 'message': 'Authentication failed'}".format(response.status_code))
            sys.exit()

    def listProjects(self):
        # To list all the projects 
        # Authentication check 
        self.authenticate()
        while not self.isProjectsLastPage:
            querystring = '?p={}&ps={}'.format(self.projectsPage, self.pageSize)
            response = requests.get(self.projects_url+querystring, auth=(self.username, self.password))
            project = response.json()
            self.projects = self.projects + project['components']
            # Each response contains total number of projects 
            # Set the last page conition to true 
            if project['paging']['total'] == len(self.projects):
                self.isProjectsLastPage = True
            # Increament the page by 1, to handle the pagination 
            self.projectsPage += 1
        return self.projects

    def downloadReports(self, reports):
        # This function writes the results to the output_dir 
        # It creates different csv files based on the self.reports keys and values 
        for key, value in reports.items():
            csv_header = value[0].keys()
            with open(self.outputFilePath+'/'+key.lower()+'.csv', 'w', newline='') as output_file:
                w = csv.writer(output_file)
                w.writerow(csv_header)
                for row in value:
                    # To remove messages received from other scanner sources
                    if not row['rule'].startswith('external'):
                        w.writerow(row.values())
            output_file.close()

    def generateReports(self, projects, type):
        self.authenticate()
        print ('Report generation: ')
        # counter is used to track the number of projects completed. It is used for percentage completion calculation 
        counter = 1
        for p in projects:
            for t in type:
                while not self.isIssuesLastPage:
                    queryString = '?componentKeys={}&s=FILE_LINE&resolved=false&types={}&p={}&ps={}'.format(p['key'] ,t, self.issuesPage, self.pageSize)
                    response = requests.get(self.issues_url+queryString, auth=(self.username, self.password))
                    issue = response.json()
                    #print('Debug: project={}, statusCode={}, issue_total={}, issue_length={}, page={}, issues_length={}'.format(p, response.status_code, issue['total'], len(issue['issues']), self.issuesPage, len(self.issues)))
                    self.issues = self.issues + issue['issues']
                    # Each response contains total number of issues  
                    # Set the last page conition to true 
                    if issue['total'] == len(self.issues):
                        self.isIssuesLastPage = True
                    self.issuesPage += 1
                self.reports[t] = self.reports[t] + self.issues
                # Set to default 
                self.issues = []
                self.isIssuesLastPage = False
                self.issuesPage = 1
            # Stdout percentage completion to keep the session interactive 
            # Number of outputs are controlled using % 10 logic 
            percentage = int(int(counter) / int(len(projects)) * 100)
            if percentage % 10 == 0:
                print('{}% complete\n'.format(percentage))
            counter += 1
        self.downloadReports(self.reports)

if __name__=="__main__":
    # Get arguments from command line 
    # -h options displays parameters used in the script 
    parser = argparse.ArgumentParser(description='SonarQube Reports')
    parser.add_argument('-H','--hostname', help='Hostname', required=True)
    parser.add_argument('-U','--username', help='Username', required=True)
    parser.add_argument('-P','--password', help='Password', required=True)
    parser.add_argument('-T','--type', help='Comma sperated values. Accepted values: BUG | CODE_SMELL | VULNERABILITY | ALL', required=False)
    parser.add_argument('-O','--output-dir', help='Output directory', required=True)
    # Arguments are stored in dictionary format 
    args = vars(parser.parse_args())
    # Check output directory exists 
    # If not terminate the script 
    if not os.path.exists(args['output_dir']):
        print('Error: Output directory does not exist or inaccessible')
        sys.exit()
    # This is to control the type argument 
    # Accepted values are BUB, CODE_SMELL, VULNERABILITY, ALL
    # If other values are received, terminate the script 
    # If type is none, defult type is set to ALL 
    accepted_values = ['BUG', 'CODE_SMELL', 'VULNERABILITY', 'ALL']
    if args['type'] is None:
        type = ['BUG', 'CODE_SMELL', 'VULNERABILITY']
        reports = {'BUG': [], 'CODE_SMELL': [], 'VULNERABILITY': []}
    else:
        type = [args['type'].upper()]
        reports = {args['type'].upper(): []}
    if type[0] not in accepted_values:
        print('Error: Invalid type value')
        sys.exit()
    # Create an object 
    sq = sonarQube(args['hostname'], args['username'], args['password'], args['output_dir'], reports)
    # listProjects returns complete projects details 
    projects = sq.listProjects()
    # generateReports process each project and its type 
    # Stores the data in self.reports using the type key 
    sq.generateReports(projects, type)