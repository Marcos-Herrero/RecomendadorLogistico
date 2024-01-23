import requests
import pandas as pd

class ReportV2():

    def __init__(self, connection, id):
        self.conn = connection
        self.base_url = connection.base_url.split('api')[0]+'/api'
        self.project_id = connection.project_id
        self.report_id = id
        self.definition = self.__get_report_def()
        self.instance_id = ''
        self.status = ''
        self.prompts = ''

    def __get_header_and_cookie(self):
        header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
        }
        header['X-MSTR-AuthToken'] = self.conn.headers['X-MSTR-AuthToken']
        cookie = dict(self.conn._session.cookies)
        return header, cookie
    
    def __get_report_def(self):
        url = self.base_url + f'/v2/reports/{self.report_id}'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.get(url, headers=h, cookies=c)
        return r

    def __instance_report(self):
        url = self.base_url + f'/v2/reports/{self.report_id}/instances'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.post(url, headers=h, cookies=c)
        return r

    def __get_prompts(self):
        url = self.base_url + f'/reports/{self.report_id}/prompts'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.get(url, headers=h, cookies=c)
        return r.json()

    def __answer_prompts(self, prompts, default=False):
        body = {'prompts':[]}
        if default:
            for p in prompts:
                a = {
                    'key':p['key'],
                    'type':p['type'],
                    'useDefault':True,
                }
                body['prompts'].append(a)
        else:
            for p in prompts:
                a = {
                    'key':p['key'],
                    'type':p['type'],
                    'answers':p['answers']
                }   
                body['prompts'].append(a)
                
        url = self.base_url + f'/reports/{self.report_id}/instances/{self.instance_id}/prompts/answers'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.put(url, headers=h, cookies=c, json=body)
        return r

    def __get_instance_status(self):
        url = self.base_url + f'/reports/{self.report_id}/instances/{self.instance_id}/status'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.get(url, headers=h, cookies=c)
        return r

    def __execute_report(self):
        url = self.base_url + f'/v2/reports/{self.report_id}/instances/{self.instance_id}'
        h, c = self.__get_header_and_cookie()
        h['X-MSTR-ProjectID'] = self.project_id
        r = requests.get(url, headers=h, cookies=c)
        return r
    
    def to_dataframe(self):
        # Instantiate Report
        instance = self.__instance_report()
        self.instance_id = instance.json()['instanceId']
        self.status = instance.json()['status']
        
        # Answer Report prompts
        if self.status == 2:  # Wating for prompt's answers
            self.prompts = self.__get_prompts()
            self.__answer_prompts(self.prompts)

        # Get report data
        data = self.__execute_report()
        definitions = data.json()['definition']['grid']['rows']
        attributes = data.json()['data']['headers']['rows']
        metrics = data.json()['data']['metricValues']['raw']
        is_total_defined = data.json()['definition']['grid']['subtotals']['defined']
        print(is_total_defined)
        # Getting columns names
        attributes_col_names = [r['name'] for r in definitions]
        metrics_col_names = [c['name'] for c in data.json()['definition']['grid']['columns'][0]['elements']]
        columns = attributes_col_names + metrics_col_names
        
        # Getting attributes values
        grid = []
        for attr in attributes:
            row = []
            # Getting attributes values
            for ix, i in enumerate(attr):
                row.append(definitions[ix]['elements'][i]['formValues'][0])   
            grid.append(row)
        
        # Getting metrics values
        for ix, r in enumerate(grid):
            grid[ix] = grid[ix]+metrics[ix]

        # Remove total row
        if is_total_defined:
            grid = grid[:-1]
    
        df = pd.DataFrame(data=grid, columns=columns)
       
        return df