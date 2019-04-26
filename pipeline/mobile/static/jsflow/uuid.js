export function random4 () {
  return Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1)
}

export function uuid (prefix = '') {
  let id = ''
  for (let i = 0; i < 7; i++) {
    id += random4()
  }
  return prefix + id
}
