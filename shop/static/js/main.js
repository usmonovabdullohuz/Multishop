/* shop.js — layk va savat: sahifani yangilamasdan, sonlar jonli yangilanadi
   Ishlatish: havola yoki forma ustiga data-ajax atributini qo'shing.
   JS o'chiq bo'lsa, havola/forma odatdagidek ishlayveradi. */
(function () {
    "use strict";

    var meta = document.querySelector('meta[name="csrf-token"]');
    var csrf = meta ? meta.content : "";

    // ---- Sonlarni yangilash (navbar + topbar) ----
    function setCount(name, value) {
        document.querySelectorAll('[data-count="' + name + '"]').forEach(function (el) {
            el.textContent = value;
            el.classList.remove("count-bump");
            void el.offsetWidth; // animatsiyani qayta ishga tushirish
            el.classList.add("count-bump");
        });
    }

    // ---- Xabar (toast) ----
    function toast(text) {
        var old = document.querySelector(".shop-toast");
        if (old) old.remove();
        var box = document.createElement("div");
        box.className = "shop-toast";
        box.textContent = text;
        document.body.appendChild(box);
        requestAnimationFrame(function () { box.classList.add("show"); });
        setTimeout(function () {
            box.classList.remove("show");
            setTimeout(function () { box.remove(); }, 400);
        }, 2200);
    }

    // ---- So'rov yuborish ----
    function send(url, body) {
        return fetch(url, {
            method: "POST",
            body: body || null,
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrf
            }
        }).then(function (res) {
            if (res.status === 401) {
                return res.json().then(function (d) { window.location.href = d.login; return null; });
            }
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        });
    }

    // ---- Javobni sahifaga qo'llash ----
    function apply(data, el) {
        if (!data) return;
        if (data.likes !== undefined) setCount("likes", data.likes);
        if (data.basket !== undefined) setCount("basket", data.basket);

        if ("liked" in data) {
            if (el) {
                el.classList.toggle("is-liked", data.liked);
                var icon = el.querySelector("i");
                if (icon) {
                    icon.classList.toggle("fas", data.liked);
                    icon.classList.toggle("far", !data.liked);
                }
                el.classList.remove("pop");
                void el.offsetWidth;
                el.classList.add("pop");
            }
            toast(data.liked ? "Yoqtirilganlarga qo'shildi ❤️" : "Yoqtirilganlardan olib tashlandi");
        }
        if (data.added) toast("Savatga qo'shildi 🛒");
    }

    // ---- Havolalar (<a data-ajax href="...">) ----
    document.addEventListener("click", function (e) {
        var el = e.target.closest("a[data-ajax], button[data-ajax][data-url]");
        if (!el) return;
        e.preventDefault();
        if (el.dataset.busy) return;
        el.dataset.busy = "1";
        var url = el.getAttribute("href") || el.dataset.url;
        send(url)
            .then(function (data) { apply(data, el); })
            .catch(function () { window.location.href = url; }) // xato bo'lsa, oddiy usulga qaytamiz
            .then(function () { delete el.dataset.busy; });
    });

    // ---- Formalar (<form data-ajax>), masalan miqdor bilan savatga qo'shish ----
    document.addEventListener("submit", function (e) {
        var form = e.target.closest("form[data-ajax]");
        if (!form) return;
        e.preventDefault();
        send(form.action, new FormData(form))
            .then(function (data) { apply(data, null); })
            .catch(function () { form.submit(); });
    });
})();