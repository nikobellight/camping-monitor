import requests

cookies = {
    'aws-waf-token': '58342482-7fe9-458b-8dfa-ffa263cde177:FAoAcWstGYkPAAAA:wswIvFPjUmECh3dfs2Y9XNza/w4GNv3JbS2IzAuH3+UCY7V5qefxSG5eg6Rre2gH4428MmEeHss1TiiKPX2R4cfKwtb7sNvvE47SzSkXj88Mzqjj9YIImk4GvST6jC8t14u61fzau1+gSsy+IyUON5c0OuE899O5u5Ry5i4/h+u08uZxDxj14eieXRWcDYc80HuKfX6TjECwTZ3eQoNineqcIunLs/fs5RsfaqGm8HJRU7L1qKdOS88tQF6wQ6bwTYA=',
    'AWSALB': 'hhXDG37qT5SMN1zCENjHDXUkQ6mkU2AjojZ72JN41uRf3Nho1WJVWluVYkyLPnpHyQ7YeVD8VTOdCQikh5cH3yxrg+RUU37uc1fbksCLxzw4Po2IDgTaUoOIyeiA',
    'AWSALBCORS': 'hhXDG37qT5SMN1zCENjHDXUkQ6mkU2AjojZ72JN41uRf3Nho1WJVWluVYkyLPnpHyQ7YeVD8VTOdCQikh5cH3yxrg+RUU37uc1fbksCLxzw4Po2IDgTaUoOIyeiA'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://marin.itinio.com/'
}

response = requests.get(
    'https://marin.itinio.com/reservation/camping/index.asp',
    cookies=cookies,
    headers=headers
)

print(f"Status code: {response.status_code}")
print(f"Response length: {len(response.text)}")
print(f"First 500 chars: {response.text[:500]}")
