import GoogleNews
from GoogleNews import GoogleNews
def noticias_covid():
    googlenews = GoogleNews()
    googlenews.setlang('es')
    googlenews.setperiod('d')
    googlenews.setencode('utf-8')
    googlenews.search('COVID-19 México')
    return googlenews.result()[6]