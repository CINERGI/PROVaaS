!function() {
    var r = null;
    (function() {
        function X(e) {
            function j() {
                try {
                    J.doScroll("left")
                } catch (e) {
                    P(j, 50);
                    return 
                }
                w("poll")
            }
            function w(j) {
                if (!(j.type == "readystatechange" && x.readyState != "complete") && ((j.type == "load" ? n : x)[z](i + j.type, w, !1), !m && (m=!0))
                    )e.call(n, j.type || j)
            }
            var Y = x.addEventListener, m=!1, C=!0, t = Y ? "addEventListener" : "attachEvent", z = Y ? "removeEventListener" : "detachEvent", i = Y ? "" : "on";
            if (x.readyState == "complete")
                e.call(n, "lazy");
            else {
                if (x.createEventObject && J.doScroll) {
                    try {
                        C=!n.frameElement
                    } catch (A) {}
                    C && j()
                }
                x[t](i + "DOMContentLoaded",
                w, !1);
                x[t](i + "readystatechange", w, !1);
                n[t](i + "load", w, !1)
            }
        }
        function Q() {
            S && X(function() {
                var e = K.length;
                $(e ? function() {
                    for (var j = 0; j < e; ++j)(function(e) {
                        P(function() {
                            n.exports[K[e]].apply(n, arguments)
                        }, 0)
                    })(j)
                } : void 0)
            })
        }
        for (var n = window, P = n.setTimeout, x = document, J = x.documentElement, L = x.head || x.getElementsByTagName("head")[0] || J, z = "", A = x.getElementsByTagName("script"), m = A.length; --m >= 0;) {
            var M = A[m], T = M.src.match(/^[^#?]*\/run_prettify\.js(\?[^#]*)?(?:#.*)?$/);
            if (T) {
                z = T[1] || "";
                M.parentNode.removeChild(M);
                break
            }
        }
        var S=!0, D = [], N = [], K = [];
        z.replace(/[&?]([^&=]+)=([^&]+)/g, function(e, j, w) {
            w = decodeURIComponent(w);
            j = decodeURIComponent(j);
            j == "autorun" ? S=!/^[0fn]/i.test(w) : j == "lang" ? D.push(w) : j == "skin" ? N.push(w) : j == "callback" && K.push(w)
        });
        m = 0;
        for (z = D.length; m < z; ++m)(function() {
            var e = x.createElement("script");
            e.onload = e.onerror = e.onreadystatechange = function() {
                if (e && (!e.readyState || /loaded|complete/.test(e.readyState)))
                    e.onerror = e.onload = e.onreadystatechange = r, --R, R || P(Q, 0), e.parentNode && e.parentNode.removeChild(e),
                e = r
            };
            e.type = "text/javascript";
            e.src = "https://google-code-prettify.googlecode.com/svn/loader/lang-" + encodeURIComponent(D[m]) + ".js";
            L.insertBefore(e, L.firstChild)
        })(D[m]);
        for (var R = D.length, A = [], m = 0, z = N.length; m < z; ++m)
            A.push("https://google-code-prettify.googlecode.com/svn/loader/skins/" + encodeURIComponent(N[m]) + ".css");
        A.push("https://google-code-prettify.googlecode.com/svn/loader/prettify.css");
        (function(e) {
            function j(m) {
                if (m !== w) {
                    var n = x.createElement("link");
                    n.rel = "stylesheet";
                    n.type = "text/css";
                    if (m + 1 < w)
                        n.error = n.onerror = function() {
                            j(m + 1)
                        };
                    n.href = e[m];
                    L.appendChild(n)
                }
            }
            var w = e.length;
            j(0)
        })(A);
        var $ = function() {
            window.PR_SHOULD_USE_CONTINUATION=!0;
            var e;
            (function() {
                function j(a) {
                    function d(f) {
                        var b = f.charCodeAt(0);
                        if (b !== 92)
                            return b;
                        var a = f.charAt(1);
                        return (b = i[a]) ? b : "0" <= a && a <= "7" ? parseInt(f.substring(1), 8) : a === "u" || a === "x" ? parseInt(f.substring(2), 16) : f.charCodeAt(1)
                    }
                    function h(f) {
                        if (f < 32)
                            return (f < 16 ? "\\x0" : "\\x") + f.toString(16);
                        f = String.fromCharCode(f);
                        return f === "\\" || f === "-" || f === "]" ||
                        f === "^" ? "\\" + f : f
                    }
                    function b(f) {
                        var b = f.substring(1, f.length-1).match(/\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2}|\\[0-3][0-7]{0,2}|\\[0-7]{1,2}|\\[\S\s]|[^\\]/g), f = [], a = b[0] === "^", c = ["["];
                        a && c.push("^");
                        for (var a = a ? 1 : 0, g = b.length; a < g; ++a) {
                            var k = b[a];
                            if (/\\[bdsw]/i.test(k))
                                c.push(k);
                            else {
                                var k = d(k), o;
                                a + 2 < g && "-" === b[a + 1] ? (o = d(b[a + 2]), a += 2) : o = k;
                                f.push([k, o]);
                                o < 65 || k > 122 || (o < 65 || k > 90 || f.push([Math.max(65, k) | 32, Math.min(o, 90) | 32]), o < 97 || k > 122 || f.push([Math.max(97, k)&-33, Math.min(o, 122)&-33]))
                            }
                        }
                        f.sort(function(f,
                        a) {
                            return f[0] - a[0] || a[1] - f[1]
                        });
                        b = [];
                        g = [];
                        for (a = 0; a < f.length; ++a)
                            k = f[a], k[0] <= g[1] + 1 ? g[1] = Math.max(g[1], k[1]) : b.push(g = k);
                        for (a = 0; a < b.length; ++a)
                            k = b[a], c.push(h(k[0])), k[1] > k[0] && (k[1] + 1 > k[0] && c.push("-"), c.push(h(k[1])));
                        c.push("]");
                        return c.join("")
                    }
                    function e(f) {
                        for (var a = f.source.match(/\[(?:[^\\\]]|\\[\S\s])*]|\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2}|\\\d+|\\[^\dux]|\(\?[!:=]|[()^]|[^()[\\^]+/g), c = a.length, d = [], g = 0, k = 0; g < c; ++g) {
                            var o = a[g];
                            o === "("?++k:
                            "\\" === o.charAt(0) && (o =+ o.substring(1)) && (o <= k ?
                            d[o] =- 1 : a[g] = h(o))
                        }
                        for (g = 1; g < d.length; ++g)
                            -1 === d[g] && (d[g]=++j);
                        for (k = g = 0; g < c; ++g)
                            o = a[g], o === "(" ? (++k, d[k] || (a[g] = "(?:")) : "\\" === o.charAt(0) && (o =+ o.substring(1)) && o <= k && (a[g] = "\\" + d[o]);
                        for (g = 0; g < c; ++g)
                            "^" === a[g] && "^" !== a[g + 1] && (a[g] = "");
                        if (f.ignoreCase && F)
                            for (g = 0; g < c; ++g)
                                o = a[g], f = o.charAt(0), o.length >= 2 && f === "[" ? a[g] = b(o) : f !== "\\" && (a[g] = o.replace(/[A-Za-z]/g, function(a) {
                            a = a.charCodeAt(0);
                            return "[" + String.fromCharCode(a&-33, a | 32) + "]"
                        }));
                        return a.join("")
                    }
                    for (var j = 0, F=!1, l=!1, I = 0, c = a.length; I < c; ++I) {
                        var p =
                        a[I];
                        if (p.ignoreCase)
                            l=!0;
                        else if (/[a-z]/i.test(p.source.replace(/\\u[\da-f]{4}|\\x[\da-f]{2}|\\[^UXux]/gi, ""))) {
                            F=!0;
                            l=!1;
                            break
                        }
                    }
                    for (var i = {
                        b: 8,
                        t: 9,
                        n: 10,
                        v: 11,
                        f: 12,
                        r: 13
                    }, q = [], I = 0, c = a.length; I < c; ++I) {
                        p = a[I];
                        if (p.global || p.multiline)
                            throw Error("" + p);
                        q.push("(?:" + e(p) + ")")
                    }
                    return RegExp(q.join("|"), l ? "gi" : "g")
                }
                function m(a, d) {
                    function h(a) {
                        var c = a.nodeType;
                        if (c == 1) {
                            if (!b.test(a.className)) {
                                for (c = a.firstChild; c; c = c.nextSibling)
                                    h(c);
                                c = a.nodeName.toLowerCase();
                                if ("br" === c || "li" === c)
                                    e[l] = "\n", F[l<<1] = j++,
                                F[l++<<1 | 1] = a
                            }
                        } else if (c == 3 || c == 4)
                            c = a.nodeValue, c.length && (c = d ? c.replace(/\r\n?/g, "\n") : c.replace(/[\t\n\r ]+/g, " "), e[l] = c, F[l<<1] = j, j += c.length, F[l++<<1 | 1] = a)
                    }
                    var b = /(?:^|\s)nocode(?:\s|$)/, e = [], j = 0, F = [], l = 0;
                    h(a);
                    return {
                        a: e.join("").replace(/\n$/, ""),
                        d: F
                    }
                }
                function n(a, d, h, b) {
                    d && (a = {
                        a: d,
                        e: a
                    }, h(a), b.push.apply(b, a.g))
                }
                function x(a) {
                    for (var d = void 0, h = a.firstChild; h; h = h.nextSibling)
                        var b = h.nodeType, d = b === 1 ? d ? a: h: b === 3 ? S.test(h.nodeValue) ? a: d: d;
                    return d === a ? void 0 : d
                }
                function C(a, d) {
                    function h(a) {
                        for (var l =
                        a.e, j = [l, "pln"], c = 0, p = a.a.match(e) || [], m = {}, q = 0, f = p.length; q < f; ++q) {
                            var B = p[q], y = m[B], u = void 0, g;
                            if (typeof y === "string")
                                g=!1;
                            else {
                                var k = b[B.charAt(0)];
                                if (k)
                                    u = B.match(k[1]), y = k[0];
                                else {
                                    for (g = 0; g < i; ++g)
                                        if (k = d[g], u = B.match(k[1])
                                            ) {
                                        y = k[0];
                                        break
                                    }
                                    u || (y = "pln")
                                }
                                if ((g = y.length >= 5 && "lang-" === y.substring(0, 5))&&!(u && typeof u[1] === "string"))
                                    g=!1, y = "src";
                                g || (m[B] = y)
                            }
                            k = c;
                            c += B.length;
                            if (g) {
                                g = u[1];
                                var o = B.indexOf(g), H = o + g.length;
                                u[2] && (H = B.length - u[2].length, o = H - g.length);
                                y = y.substring(5);
                                n(l + k, B.substring(0, o), h,
                                j);
                                n(l + k + o, g, A(y, g), j);
                                n(l + k + H, B.substring(H), h, j)
                            } else 
                                j.push(l + k, y)
                        }
                        a.g = j
                    }
                    var b = {}, e;
                    (function() {
                        for (var h = a.concat(d), l = [], i = {}, c = 0, p = h.length; c < p; ++c) {
                            var m = h[c], q = m[3];
                            if (q)
                                for (var f = q.length; --f >= 0;)
                                    b[q.charAt(f)] = m;
                            m = m[1];
                            q = "" + m;
                            i.hasOwnProperty(q) || (l.push(m), i[q] = r)
                        }
                        l.push(/[\S\s]/);
                        e = j(l)
                    })();
                    var i = d.length;
                    return h
                }
                function t(a) {
                    var d = [], h = [];
                    a.tripleQuotedStrings ? d.push(["str", /^(?:'''(?:[^'\\]|\\[\S\s]|''?(?=[^']))*(?:'''|$)|"""(?:[^"\\]|\\[\S\s]|""?(?=[^"]))*(?:"""|$)|'(?:[^'\\]|\\[\S\s])*(?:'|$)|"(?:[^"\\]|\\[\S\s])*(?:"|$))/,
                    r, "'\""]) : a.multiLineStrings ? d.push(["str", /^(?:'(?:[^'\\]|\\[\S\s])*(?:'|$)|"(?:[^"\\]|\\[\S\s])*(?:"|$)|`(?:[^\\`]|\\[\S\s])*(?:`|$))/, r, "'\"`"]) : d.push(["str", /^(?:'(?:[^\n\r'\\]|\\.)*(?:'|$)|"(?:[^\n\r"\\]|\\.)*(?:"|$))/, r, "\"'"]);
                    a.verbatimStrings && h.push(["str", /^@"(?:[^"]|"")*(?:"|$)/, r]);
                    var b = a.hashComments;
                    b && (a.cStyleComments ? (b > 1 ? d.push(["com", /^#(?:##(?:[^#]|#(?!##))*(?:###|$)|.*)/, r, "#"]) : d.push(["com", /^#(?:(?:define|e(?:l|nd)if|else|error|ifn?def|include|line|pragma|undef|warning)\b|[^\n\r]*)/,
                    r, "#"]), h.push(["str", /^<(?:(?:(?:\.\.\/)*|\/?)(?:[\w-]+(?:\/[\w-]+)+)?[\w-]+\.h(?:h|pp|\+\+)?|[a-z]\w*)>/, r])) : d.push(["com", /^#[^\n\r]*/, r, "#"]));
                    a.cStyleComments && (h.push(["com", /^\/\/[^\n\r]*/, r]), h.push(["com", /^\/\*[\S\s]*?(?:\*\/|$)/, r]));
                    if (b = a.regexLiterals) {
                        var e = (b = b > 1 ? "" : "\n\r") ? ".": "[\\S\\s]";
                        h.push(["lang-regex", RegExp("^(?:^^\\.?|[+-]|[!=]=?=?|\\#|%=?|&&?=?|\\(|\\*=?|[+\\-]=|->|\\/=?|::?|<<?=?|>>?>?=?|,|;|\\?|@|\\[|~|{|\\^\\^?=?|\\|\\|?=?|break|case|continue|delete|do|else|finally|instanceof|return|throw|try|typeof)\\s*(" +
                        ("/(?=[^/*" + b + "])(?:[^/\\x5B\\x5C" + b + "]|\\x5C" + e + "|\\x5B(?:[^\\x5C\\x5D" + b + "]|\\x5C" + e + ")*(?:\\x5D|$))+/") + ")")])
                    }(b = a.types) && h.push(["typ", b]);
                    b = ("" + a.keywords).replace(/^ | $/g, "");
                    b.length && h.push(["kwd", RegExp("^(?:" + b.replace(/[\s,]+/g, "|") + ")\\b"), r]);
                    d.push(["pln", /^\s+/, r, " \r\n\t\u00a0"]);
                    b = "^.[^\\s\\w.$@'\"`/\\\\]*";
                    a.regexLiterals && (b += "(?!s*/)");
                    h.push(["lit", /^@[$_a-z][\w$@]*/i, r], ["typ", /^(?:[@_]?[A-Z]+[a-z][\w$@]*|\w+_t\b)/, r], ["pln", /^[$_a-z][\w$@]*/i, r], ["lit", /^(?:0x[\da-f]+|(?:\d(?:_\d+)*\d*(?:\.\d*)?|\.\d\+)(?:e[+-]?\d+)?)[a-z]*/i,
                    r, "0123456789"], ["pln", /^\\[\S\s]?/, r], ["pun", RegExp(b), r]);
                    return C(d, h)
                }
                function z(a, d, h) {
                    function b(a) {
                        var c = a.nodeType;
                        if (c == 1&&!j.test(a.className))
                            if ("br" === a.nodeName)
                                e(a), a.parentNode && a.parentNode.removeChild(a);
                        else 
                            for (a = a.firstChild; a; a = a.nextSibling)
                                b(a);
                            else if ((c == 3 || c == 4) && h) {
                                var d = a.nodeValue, i = d.match(m);
                                if (i)
                                    c = d.substring(0, i.index), a.nodeValue = c, (d = d.substring(i.index + i[0].length)) && a.parentNode.insertBefore(l.createTextNode(d), a.nextSibling), e(a), c || a.parentNode.removeChild(a)
                            }
                    }
                    function e(a) {
                        function b(a, c) {
                            var d = c ? a.cloneNode(!1): a, f = a.parentNode;
                            if (f) {
                                var f = b(f, 1), h = a.nextSibling;
                                f.appendChild(d);
                                for (var e = h; e; e = h)
                                    h = e.nextSibling, f.appendChild(e)
                            }
                            return d
                        }
                        for (; !a.nextSibling;)
                            if (a = a.parentNode, !a)
                                return;
                        for (var a = b(a.nextSibling, 0), d; (d = a.parentNode) && d.nodeType === 1;)
                            a = d;
                        c.push(a)
                    }
                    for (var j = /(?:^|\s)nocode(?:\s|$)/, m = /\r\n?|\n/, l = a.ownerDocument, i = l.createElement("li"); a.firstChild;)
                        i.appendChild(a.firstChild);
                    for (var c = [i], p = 0; p < c.length; ++p)
                        b(c[p]);
                    d === (d | 0) && c[0].setAttribute("value",
                    d);
                    var n = l.createElement("ol");
                    n.className = "linenums";
                    for (var d = Math.max(0, d-1 | 0) || 0, p = 0, q = c.length; p < q; ++p)
                        i = c[p], i.className = "L" + (p + d)%10, i.firstChild || i.appendChild(l.createTextNode("\u00a0")), n.appendChild(i);
                    a.appendChild(n)
                }
                function i(a, d) {
                    for (var h = d.length; --h >= 0;) {
                        var b = d[h];
                        U.hasOwnProperty(b) ? V.console && console.warn("cannot override language handler %s", b) : U[b] = a
                    }
                }
                function A(a, d) {
                    if (!a ||!U.hasOwnProperty(a))
                        a = /^\s*</.test(d) ? "default-markup" : "default-code";
                    return U[a]
                }
                function D(a) {
                    var d =
                    a.h;
                    try {
                        var h = m(a.c, a.i), b = h.a;
                        a.a = b;
                        a.d = h.d;
                        a.e = 0;
                        A(d, b)(a);
                        var e = /\bMSIE\s(\d+)/.exec(navigator.userAgent), e = e&&+e[1] <= 8, d = /\n/g, i = a.a, j = i.length, h = 0, l = a.d, n = l.length, b = 0, c = a.g, p = c.length, t = 0;
                        c[p] = j;
                        var q, f;
                        for (f = q = 0; f < p;)
                            c[f] !== c[f + 2] ? (c[q++] = c[f++], c[q++] = c[f++]) : f += 2;
                        p = q;
                        for (f = q = 0; f < p;) {
                            for (var x = c[f], y = c[f + 1], u = f + 2; u + 2 <= p && c[u + 1] === y;)
                                u += 2;
                            c[q++] = x;
                            c[q++] = y;
                            f = u
                        }
                        c.length = q;
                        var g = a.c, k;
                        if (g)
                            k = g.style.display, g.style.display = "none";
                        try {
                            for (; b < n;) {
                                var o = l[b + 2] || j, H = c[t + 2] || j, u = Math.min(o, H), E = l[b +
                                1], W;
                                if (E.nodeType !== 1 && (W = i.substring(h, u))) {
                                    e && (W = W.replace(d, "\r"));
                                    E.nodeValue = W;
                                    var Z = E.ownerDocument, s = Z.createElement("span");
                                    s.className = c[t + 1];
                                    var z = E.parentNode;
                                    z.replaceChild(s, E);
                                    s.appendChild(E);
                                    h < o && (l[b + 1] = E = Z.createTextNode(i.substring(u, o)), z.insertBefore(E, s.nextSibling))
                                }
                                h = u;
                                h >= o && (b += 2);
                                h >= H && (t += 2)
                            }
                        } finally {
                            if (g)
                                g.style.display = k
                        }
                    } catch (v) {
                        V.console && console.log(v && v.stack || v)
                    }
                }
                var V = window, G = ["break,continue,do,else,for,if,return,while"], O = [[G, "auto,case,char,const,default,double,enum,extern,float,goto,inline,int,long,register,short,signed,sizeof,static,struct,switch,typedef,union,unsigned,void,volatile"],
                "catch,class,delete,false,import,new,operator,private,protected,public,this,throw,true,try,typeof"], J = [O, "alignof,align_union,asm,axiom,bool,concept,concept_map,const_cast,constexpr,decltype,delegate,dynamic_cast,explicit,export,friend,generic,late_check,mutable,namespace,nullptr,property,reinterpret_cast,static_assert,static_cast,template,typeid,typename,using,virtual,where"], K = [O, "abstract,assert,boolean,byte,extends,final,finally,implements,import,instanceof,interface,null,native,package,strictfp,super,synchronized,throws,transient"],
                L = [K, "as,base,by,checked,decimal,delegate,descending,dynamic,event,fixed,foreach,from,group,implicit,in,internal,into,is,let,lock,object,out,override,orderby,params,partial,readonly,ref,sbyte,sealed,stackalloc,string,select,uint,ulong,unchecked,unsafe,ushort,var,virtual,where"], O = [O, "debugger,eval,export,function,get,null,set,undefined,var,with,Infinity,NaN"], M = [G, "and,as,assert,class,def,del,elif,except,exec,finally,from,global,import,in,is,lambda,nonlocal,not,or,pass,print,raise,try,with,yield,False,True,None"],
                N = [G, "alias,and,begin,case,class,def,defined,elsif,end,ensure,false,in,module,next,nil,not,or,redo,rescue,retry,self,super,then,true,undef,unless,until,when,yield,BEGIN,END"], R = [G, "as,assert,const,copy,drop,enum,extern,fail,false,fn,impl,let,log,loop,match,mod,move,mut,priv,pub,pure,ref,self,static,struct,true,trait,type,unsafe,use"], G = [G, "case,done,elif,esac,eval,fi,function,in,local,set,then,until"], Q = /^(DIR|FILE|vector|(de|priority_)?queue|list|stack|(const_)?iterator|(multi)?(set|map)|bitset|u?(int|float)\d*)\b/,
                S = /\S/, T = t({
                    keywords: [J, L, O, "caller,delete,die,do,dump,elsif,eval,exit,foreach,for,goto,if,import,last,local,my,next,no,our,print,package,redo,require,sub,undef,unless,until,use,wantarray,while,BEGIN,END", M, N, G],
                    hashComments: !0,
                    cStyleComments: !0,
                    multiLineStrings: !0,
                    regexLiterals: !0
                }), U = {};
                i(T, ["default-code"]);
                i(C([], [["pln", /^[^<?]+/], ["dec", /^<!\w[^>]*(?:>|$)/], ["com", /^<\!--[\S\s]*?(?:--\>|$)/], ["lang-", /^<\?([\S\s]+?)(?:\?>|$)/], ["lang-", /^<%([\S\s]+?)(?:%>|$)/], ["pun", /^(?:<[%?]|[%?]>)/], ["lang-",
                /^<xmp\b[^>]*>([\S\s]+?)<\/xmp\b[^>]*>/i], ["lang-js", /^<script\b[^>]*>([\S\s]*?)(<\/script\b[^>]*>)/i], ["lang-css", /^<style\b[^>]*>([\S\s]*?)(<\/style\b[^>]*>)/i], ["lang-in.tag", /^(<\/?[a-z][^<>]*>)/i]]), ["default-markup", "htm", "html", "mxml", "xhtml", "xml", "xsl"]);
                i(C([["pln", /^\s+/, r, " \t\r\n"], ["atv", /^(?:"[^"]*"?|'[^']*'?)/, r, "\"'"]], [["tag", /^^<\/?[a-z](?:[\w-.:]*\w)?|\/?>$/i], ["atn", /^(?!style[\s=]|on)[a-z](?:[\w:-]*\w)?/i], ["lang-uq.val", /^=\s*([^\s"'>]*(?:[^\s"'/ > ] | \ / (?=\s))) / ], ["pun", /^[/<->] + /],
                ["lang-js", /^on\w+\s*=\s*"([^"]+)"/i], ["lang-js", /^on\w+\s*=\s*'([^']+)'/i], ["lang-js", /^on\w+\s*=\s*([^\s"'>]+)/i], ["lang-css", /^style\s*=\s*"([^"]+)"/i], ["lang-css", /^style\s*=\s*'([^']+)'/i], ["lang-css", /^style\s*=\s*([^\s"'>]+)/i]]), ["in.tag"]);
                i(C([], [["atv", /^[\S\s]+/]]), ["uq.val"]);
                i(t({
                    keywords: J,
                    hashComments: !0,
                    cStyleComments: !0,
                    types: Q
                }), ["c", "cc", "cpp", "cxx", "cyc", "m"]);
                i(t({
                    keywords: "null,true,false"
                }), ["json"]);
                i(t({
                    keywords: L,
                    hashComments: !0,
                    cStyleComments: !0,
                    verbatimStrings: !0,
                    types: Q
                }),
                ["cs"]);
                i(t({
                    keywords: K,
                    cStyleComments: !0
                }), ["java"]);
                i(t({
                    keywords: G,
                    hashComments: !0,
                    multiLineStrings: !0
                }), ["bash", "bsh", "csh", "sh"]);
                i(t({
                    keywords: M,
                    hashComments: !0,
                    multiLineStrings: !0,
                    tripleQuotedStrings: !0
                }), ["cv", "py", "python"]);
                i(t({
                    keywords: "caller,delete,die,do,dump,elsif,eval,exit,foreach,for,goto,if,import,last,local,my,next,no,our,print,package,redo,require,sub,undef,unless,until,use,wantarray,while,BEGIN,END",
                    hashComments: !0,
                    multiLineStrings: !0,
                    regexLiterals: 2
                }), ["perl", "pl", "pm"]);
                i(t({
                    keywords: N,
                    hashComments: !0,
                    multiLineStrings: !0,
                    regexLiterals: !0
                }), ["rb", "ruby"]);
                i(t({
                    keywords: O,
                    cStyleComments: !0,
                    regexLiterals: !0
                }), ["javascript", "js"]);
                i(t({
                    keywords: "all,and,by,catch,class,else,extends,false,finally,for,if,in,is,isnt,loop,new,no,not,null,of,off,on,or,return,super,then,throw,true,try,unless,until,when,while,yes",
                    hashComments: 3,
                    cStyleComments: !0,
                    multilineStrings: !0,
                    tripleQuotedStrings: !0,
                    regexLiterals: !0
                }), ["coffee"]);
                i(t({
                    keywords: R,
                    cStyleComments: !0,
                    multilineStrings: !0
                }), ["rc", "rs", "rust"]);
                i(C([], [["str", /^[\S\s]+/]]), ["regex"]);
                var X = V.PR = {
                    createSimpleLexer: C,
                    registerLangHandler: i,
                    sourceDecorator: t,
                    PR_ATTRIB_NAME: "atn",
                    PR_ATTRIB_VALUE: "atv",
                    PR_COMMENT: "com",
                    PR_DECLARATION: "dec",
                    PR_KEYWORD: "kwd",
                    PR_LITERAL: "lit",
                    PR_NOCODE: "nocode",
                    PR_PLAIN: "pln",
                    PR_PUNCTUATION: "pun",
                    PR_SOURCE: "src",
                    PR_STRING: "str",
                    PR_TAG: "tag",
                    PR_TYPE: "typ",
                    prettyPrintOne: function(a, d, e) {
                        var b = document.createElement("div");
                        b.innerHTML = "<pre>" + a + "</pre>";
                        b = b.firstChild;
                        e && z(b, e, !0);
                        D({
                            h: d,
                            j: e,
                            c: b,
                            i: 1
                        });
                        return b.innerHTML
                    },
                    prettyPrint: e = e = function(a, d) {
                        function e() {
                            for (var b = V.PR_SHOULD_USE_CONTINUATION ? c.now() + 250 : Infinity; p < j.length && c.now() < b; p++) {
                                for (var d = j[p], m = k, l = d; l = l.previousSibling;) {
                                    var n = l.nodeType, s = (n === 7 || n === 8) && l.nodeValue;
                                    if (s?!/^\??prettify\b/.test(s) : n !== 3 || /\S/.test(l.nodeValue)
                                        )break;
                                    if (s) {
                                        m = {};
                                        s.replace(/\b(\w+)=([\w%+\-.:]+)/g, function(a, b, c) {
                                            m[b] = c
                                        });
                                        break
                                    }
                                }
                                l = d.className;
                                if ((m !== k || f.test(l))&&!w.test(l)) {
                                    n=!1;
                                    for (s = d.parentNode; s; s = s.parentNode)
                                        if (g.test(s.tagName) && s.className && f.test(s.className)) {
                                            n =
                                            !0;
                                            break
                                        }
                                    if (!n) {
                                        d.className += " prettyprinted";
                                        n = m.lang;
                                        if (!n) {
                                            var n = l.match(q), A;
                                            if (!n && (A = x(d)) && u.test(A.tagName))
                                                n = A.className.match(q);
                                            n && (n = n[1])
                                        }
                                        if (y.test(d.tagName))
                                            s = 1;
                                        else 
                                            var s = d.currentStyle, v = i.defaultView, s = (s = s ? s.whiteSpace : v && v.getComputedStyle ? v.getComputedStyle(d, r).getPropertyValue("white-space") : 0) && "pre" === s.substring(0, 3);
                                        v = m.linenums;
                                        if (!(v = v === "true"||+v))
                                            v = (v = l.match(/\blinenums\b(?::(\d+))?/)) ? v[1] && v[1].length?+v[1] : !0 : !1;
                                        v && z(d, v, s);
                                        t = {
                                            h: n,
                                            c: d,
                                            j: v,
                                            i: s
                                        };
                                        D(t)
                                    }
                                }
                            }
                            p < j.length ?
                            P(e, 250) : "function" === typeof a && a()
                        }
                        for (var b = d || document.body, i = b.ownerDocument || document, b = [b.getElementsByTagName("pre"), b.getElementsByTagName("code"), b.getElementsByTagName("xmp")], j = [], m = 0; m < b.length; ++m)
                            for (var l = 0, n = b[m].length; l < n; ++l)
                                j.push(b[m][l]);
                        var b = r, c = Date;
                        c.now || (c = {
                            now: function() {
                                return + new Date
                            }
                        });
                        var p = 0, t, q = /\blang(?:uage)?-([\w.]+)(?!\S)/, f = /\bprettyprint\b/, w = /\bprettyprinted\b/, y = /pre|xmp/i, u = /^code$/i, g = /^(?:pre|code|xmp)$/i, k = {};
                        e()
                    }
                };
                typeof define === "function" && define.amd &&
                define("google-code-prettify", [], function() {
                    return X
                })
            })();
            return e
        }();
        R || P(Q, 0)
    })();
}()
