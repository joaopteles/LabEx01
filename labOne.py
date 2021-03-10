import json
import requests
from csv import writer
import os
import os.path

def executar_query_github(query):
    request = requests.post('https://api.github.com/graphql', json = {'query': query}, headers = headers)
    if request.status_code == 200:
        return request.json()
    elif request.status_code == 502:
      return executar_query_github(query)
    else:
        raise Exception("A query falhou: {}. {}".format(request.status_code, query))

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer API_KEY_GITHUB'
}

query = """
query LabOne {
  search(query: "stars:>100", type: REPOSITORY, first: 10 {endCursorCode} ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        url
        createdAt
        updatedAt
        pullRequestsAceitas: pullRequests(states: MERGED){ totalCount }
        pullRequests {
          totalCount
        }
        releases(first: 10) {
          totalCount
        }
        primaryLanguage {
          name
        }
        closed: issues(first: 10, states: CLOSED) {
          totalCount
        }
        total: issues(first: 10) {
          totalCount
        }
      }
    }
  }
}
"""

def formatar_datas(response):
    nodes = response['data']['search']['nodes']
    for i, repositorio in enumerate(nodes):
        nodes[i]['createdAt'] = nodes[i]['createdAt'].split("T")[0]
        nodes[i]['updatedAt'] = nodes[i]['updatedAt'].split("T")[0]

        
query_inicial = query.replace("{endCursorCode}", "")
response = executar_query_github(query_inicial)
quantidade_execucoes = 1 
formatar_datas(response)
todos_resultados = response["data"]["search"]["nodes"]
end_cursor = response["data"]["search"]["pageInfo"]["endCursor"]
has_next_page = response["data"]["search"]["pageInfo"]["hasNextPage"]

while (quantidade_execucoes < 100 and has_next_page):
    proxima_query = query.replace("{endCursorCode}", ', after: "%s"' % end_cursor)
    response = executar_query_github(proxima_query)
    formatar_datas(response)
    todos_resultados += response["data"]["search"]["nodes"] 
    quantidade_execucoes += 1
    has_next_page = response["data"]["search"]["pageInfo"]["hasNextPage"] 
    end_cursor = response["data"]["search"]["pageInfo"]["endCursor"] 

def exportar_para_csv(data):
    pathRelativa = os.getcwd() + "\output_repositorios_github.csv"
    with open(pathRelativa, 'w+') as csv_final:
        csvWriter = writer(csv_final)
        header = (["Nome", "URL", "Criado em", "Atualizado em","Quantidade de stars", "Pull Requests aceitas", "Pull Requests totais", "Releases", "Linguagem primária", "Issues fechadas","Todas Issues"])
        csvWriter.writerow(header)
        for repo in data:
            repoRow =([repo['nameWithOwner'],repo['url'], repo['createdAt'], repo['updatedAt'],repo['stargazerCount'], repo['pullRequestsAceitas'], repo['pullRequests'],repo['releases'], repo['primaryLanguage'], repo['closed'], repo['total']])
            csvWriter.writerow(repoRow)


exportar_para_csv(todos_resultados)