import EncryptJS from 'jsencrypt'
import { b64tohex, hex2b64 } from 'jsencrypt/lib/lib/jsbn/base64'

export default class EncryptRSA {
    constructor () {
        this.instance = new EncryptJS()
        this.publicKey = ''
    }
    // 设置公钥
    setPublicKey (publicKey) {
        this.publicKey = publicKey
        this.instance.setPublicKey(publicKey)
    }
    setPrivateKey (privateKey) {
        this.instance.setPrivateKey(privateKey)
    }
    getKey () {
        return this.instance.getKey()
    }
    getKeyLength () {
        const key = this.getKey()
        return ((key.n.bitLength() + 7) >> 3)
    }
    getChunkLength () {
        // 根据key所能编码的最大长度来定分段长度。 key size - 11：11字节随机padding使每次加密结果都不同。
        return this.getKeyLength() - 11
    }
    // 普通加密 返回的是base64编码字符串(长字符串不可加密)
    encrypt (string) {
        if (!this.publicKey) {
            console.warn('The public key is empty!')
            return ''
        }
        return this.instance.encrypt(string)
    }
    // 普通解密 需设置私钥(长字符串不可解密)
    decrypt (msg) {
        return this.instance.decrypt(msg)
    }
    // 分段加密
    encryptChunk (text) {
        const k = this.getKey()
        const chunkLength = this.getChunkLength()

        try {
            let subStr = ''
            let decrypted = ''
            let subStart = 0
            let subEnd = 0
            let bitLen = 0
            let tmpPoint = 0
            const string = `${text}`
            const strLen = string.length
            for (let i = 0; i < strLen; i++) {
                // js 是使用 Unicode 编码的，每个字符所占用的字节数不同
                const charCode = string.charCodeAt(i)
                if (charCode <= 0x007f) {
                    bitLen += 1
                } else if (charCode <= 0x07ff) {
                    bitLen += 2
                } else if (charCode <= 0xffff) {
                    bitLen += 3
                } else {
                    bitLen += 4
                }
                // 字节数到达上限，获取子字符串加密并追加到总字符串后。更新下一个字符串起始位置及字节计算。
                if (bitLen > chunkLength) {
                    subStr = string.substring(subStart, subEnd)
                    decrypted += k.encrypt(subStr) // 加密差异点
                    subStart = subEnd
                    bitLen = bitLen - tmpPoint
                } else {
                    subEnd = i
                    tmpPoint = bitLen
                }
            }
            subStr = string.substring(subStart, strLen)
            decrypted += k.encrypt(subStr)
            return hex2b64(decrypted)
        } catch (err) {
            console.warn(err)
            return ''
        }
    }
    // 分段解密
    decryptChunk (string) {
        const k = this.getKey()
        // 解密长度=key size.hex2b64结果是每字节每两字符，所以直接*2
        const maxDecryptBlock = this.getKeyLength() * 2
        try {
            const hexString = b64tohex(`${string}`)
            let decrypted = ''
            const rexStr = `.{1,${maxDecryptBlock}}`
            const rex = new RegExp(rexStr, 'g')
            const subStrArray = hexString.match(rex)
            if (subStrArray) {
                subStrArray.forEach((entry) => {
                    decrypted += k.decrypt(entry) // 解密差异点
                })
            }
            return decrypted
        } catch (err) {
            console.warn(err)
            return ''
        }
    }
}
