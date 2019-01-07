import urlfetch
url = "https://api.quovo.com/v3/accounts/18298981/transactions"

#headers = "Authorization: Bearer 0d180d0c1b3cbb37312752fde85bbe4ed4e54e58df2987d47481d360e60080e5"
result = urlfetch.fetch(
        url=url,
        headers= {"Authorization": "Bearer 0d180d0c1b3cbb37312752fde85bbe4ed4e54e58df2987d47481d360e60080e5"})
print(result.content)
