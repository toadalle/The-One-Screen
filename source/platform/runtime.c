#include <stddef.h>
#include <stdint.h>
void* memcpy(void* dst,const void* src,size_t n){unsigned char* d=dst;const unsigned char* s=src;while(n--)*d++=*s++;return dst;}
void* memset(void* dst,int c,size_t n){unsigned char* d=dst;while(n--)*d++=(unsigned char)c;return dst;}
void __aeabi_memcpy(void* d,const void* s,size_t n){memcpy(d,s,n);}
void __aeabi_memcpy4(void* d,const void* s,size_t n){memcpy(d,s,n);}
void __aeabi_memclr(void* d,size_t n){memset(d,0,n);}
void __aeabi_memclr4(void* d,size_t n){memset(d,0,n);}
uint32_t __aeabi_uidiv(uint32_t n,uint32_t d){
    if(!d)return 0;uint32_t q=0;
    for(int i=31;i>=0;i--)if((n>>i)>=d){n-=d<<i;q|=1u<<i;}
    return q;
}
