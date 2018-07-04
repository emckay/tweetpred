'use strict';

module.exports.generate_predictions = async (event, context, callback) => {
  const rootUrl = 'https://xdtgo0825j.execute-api.us-west-2.amazonaws.com/dev/tw'
  const fetch = require('node-fetch')
  const postReq = (url, body, errCb) =>
    fetch(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(body)
      }
    )
      .then((res) => res.json())
      .catch((err) => errCb(err))
  const accounts = await fetch(`${rootUrl}/accounts/`).then((res) => res.json())
  const account = accounts.find((account) => account.screen_name === event.screen_name)
  const data_file = await postReq(`${rootUrl}/data_files/`, { account_id: account.pk }, callback)
  const estimate = await postReq(`${rootUrl}/estimates/`, { data_file_id: data_file.pk }, callback)
  const promises = []
  for (let i = 0; i < 5; i++) {
    promises.push(postReq(`${rootUrl}/predictions/`, { data_file_id: data_file.pk, estimate_id: estimate.pk, n: 50 }, callback))
  }
  await Promise.all(promises)
  callback(null, 'finished successfully')
}
