import axios from 'axios'

export default axios.create({
  baseURL: 'https://xdtgo0825j.execute-api.us-west-2.amazonaws.com/dev/tw/',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})
