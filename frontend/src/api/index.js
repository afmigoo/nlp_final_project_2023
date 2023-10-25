import instance from './instance'
import searchModule from './search'

export default {
    search: searchModule(instance)
}