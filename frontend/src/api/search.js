export default function (instance) {
    return {
        findGrams(payload) {
            return instance.post('api/find', payload)
        },
        widenContext(payload) {
            return instance.post('api/context', payload)
        }
    }
}