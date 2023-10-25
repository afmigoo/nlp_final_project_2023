import axios from 'axios'


const instance = axios.create({
    baseURL: process.env.VUE_APP_API_URL,
    headers: {
        accept: 'application/json'
    }
})

console.log(process.env.VUE_APP_API_URL)

export default instance