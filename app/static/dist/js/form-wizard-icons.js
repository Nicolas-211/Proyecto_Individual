"use strict";
$(function() {
    var e = $(".select2")
      , t = $(".selectpicker");
    t.length && t.selectpicker(),
    e.length && e.each(function() {
        var e = $(this);
        e.wrap('<div class="position-relative"></div>'),
        e.select2({
            placeholder: "Select value",
            dropdownParent: e.parent()
        })
    })
}),
function() {
    var e = document.querySelector(".wizard-icons-example");
    if (null !== e) {
        var t = [].slice.call(e.querySelectorAll(".btn-next"))
          , l = [].slice.call(e.querySelectorAll(".btn-prev"))
          , r = e.querySelector(".btn-submit");
        const c = new Stepper(e,{
            linear: !1
        });
        t && t.forEach(e=>{
            e.addEventListener("click", e=>{
                c.next()
            }
            )
        }
        ),
        l && l.forEach(e=>{
            e.addEventListener("click", e=>{
                c.previous()
            }
            )
        }
        ),
        r && r.addEventListener("click", e=>{
            alert("Submitted..!!")
        }
        )
    }
    e = document.querySelector(".wizard-vertical-icons-example");
    if (null !== e) {
        t = [].slice.call(e.querySelectorAll(".btn-next")),
        l = [].slice.call(e.querySelectorAll(".btn-prev")),
        r = e.querySelector(".btn-submit");
        const n = new Stepper(e,{
            linear: !1
        });
        t && t.forEach(e=>{
            e.addEventListener("click", e=>{
                n.next()
            }
            )
        }
        ),
        l && l.forEach(e=>{
            e.addEventListener("click", e=>{
                n.previous()
            }
            )
        }
        ),
        r && r.addEventListener("click", e=>{
            alert("Submitted..!!")
        }
        )
    }
    e = document.querySelector(".wizard-modern-icons-example");
    if (null !== e) {
        t = [].slice.call(e.querySelectorAll(".btn-next")),
        l = [].slice.call(e.querySelectorAll(".btn-prev")),
        r = e.querySelector(".btn-submit");
        const i = new Stepper(e,{
            linear: !1
        });
        t && t.forEach(e=>{
            e.addEventListener("click", e=>{
                i.next()
            }
            )
        }
        ),
        l && l.forEach(e=>{
            e.addEventListener("click", e=>{
                i.previous()
            }
            )
        }
        ),
        r && r.addEventListener("click", e=>{
            alert("Submitted..!!")
        }
        )
    }
    e = document.querySelector(".wizard-modern-vertical-icons-example");
    if (null !== e) {
        t = [].slice.call(e.querySelectorAll(".btn-next")),
        l = [].slice.call(e.querySelectorAll(".btn-prev")),
        r = e.querySelector(".btn-submit");
        const a = new Stepper(e,{
            linear: !1
        });
        t && t.forEach(e=>{
            e.addEventListener("click", e=>{
                a.next()
            }
            )
        }
        ),
        l && l.forEach(e=>{
            e.addEventListener("click", e=>{
                a.previous()
            }
            )
        }
        ),
        r && r.addEventListener("click", e=>{
            alert("Submitted..!!")
        }
        )
    }
}();
