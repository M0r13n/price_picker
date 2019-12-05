var padding = {top: 20, right: 40, bottom: 0, left: 0},
    w = 500 - padding.left - padding.right,
    h = 500 - padding.top - padding.bottom,
    r = Math.min(w, h) / 2,
    rotation = 0,
    oldrotation = 0,
    picked = 100000,
    firstSpin = true,
    url = '/wof/submit',
    color = d3.scale.category20();

var data = [
    {label: "5€ Rabatt", value: 1, question: "Hurraa! Dein Rabattcode: "},
    {label: "Leider nichts", value: 0, question: "Leider Pech gehabt."},
    {label: "Pech gehabt", value: 0, question: "Leider Pech gehabt."},
    {label: "5€ Rabatt", value: 1, question: "Hurraa! Dein Rabattcode: "},
    {label: "5€ Rabatt", value: 1, question: "Hurraa! Dein Rabattcode: "},
    {label: "Knapp daneben", value: 0, question: "Leider Pech gehabt."},
    {label: "Ooops", value: 0, question: "Leider Pech gehabt."},
    {label: "5€ Rabatt", value: 1, question: "Hurraa! Dein Rabattcode: "}
];

var svg = d3
    .select("#chart")
    .append("svg")
    .data([data])
    .attr("width", w + padding.left + padding.right)
    .attr("height", h + padding.top + padding.bottom);

var container = svg
    .append("g")
    .attr("class", "chartholder")
    .attr(
        "transform",
        "translate(" +
        (w / 2 + padding.left) +
        "," +
        (h / 2 + padding.top) +
        ")"
    );

var vis = container.append("g");

var pie = d3.layout
    .pie()
    .sort(null)
    .value(function (d) {
        return 1;
    });

// declare an arc generator function
var arc = d3.svg.arc().outerRadius(r);

// select paths, use arc generator to draw
var arcs = vis
    .selectAll("g.slice")
    .data(pie)
    .enter()
    .append("g")
    .attr("class", "slice");

arcs
    .append("path")
    .attr("fill", function (d, i) {
        return color(i);
    })
    .attr("d", function (d) {
        return arc(d);
    });

// add the text
arcs
    .append("text")
    .attr("transform", function (d) {
        d.innerRadius = 0;
        d.outerRadius = r;
        d.angle = (d.startAngle + d.endAngle) / 2;
        return (
            "rotate(" +
            ((d.angle * 180) / Math.PI - 90) +
            ")translate(" +
            (d.outerRadius - 10) +
            ")"
        );
    })
    .attr("text-anchor", "end")
    .text(function (d, i) {
        return data[i].label;
    });

//container.on("click", spin);

function spin(code) {
    if (!firstSpin) {
        return;
    }
    container.on("click", null);

    var ps = 360 / data.length,
        pieslice = Math.round(1440 / data.length),
        rng = Math.floor(Math.random() * 1440 + 360);

    rotation = Math.round(rng / ps) * ps;

    picked = Math.round(data.length - (rotation % 360) / ps);
    picked = picked >= data.length ? picked % data.length : picked;

    rotation += 90 - Math.round(ps / 2);

    vis
        .transition()
        .duration(3000)
        .attrTween("transform", rotTween)
        .each("end", function () {
            //populate question
            var result = data[picked];

            var text = result.question;

            if (result.value === 1) {
                text += code;
            }
            d3.select("#question h1").text(text)
        });
    firstSpin = false;
}

//make arrow
svg
    .append("g")
    .attr(
        "transform",
        "translate(" +
        (w + padding.left + padding.right) +
        "," +
        (h / 2 + padding.top) +
        ")"
    )
    .append("path")
    .attr(
        "d",
        "M-" + r * 0.15 + ",0L0," + r * 0.05 + "L0,-" + r * 0.05 + "Z"
    )
    .style({fill: "black"});

//draw spin circle
container
    .append("circle")
    .attr("cx", 0)
    .attr("cy", 0)
    .attr("r", 60)
    .style({fill: "white", cursor: "pointer"});

function rotTween(to) {
    var i = d3.interpolate(oldrotation % 360, rotation);
    return function (t) {
        return "rotate(" + i(t) + ")";
    };
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


function displayWheel() {
    if (getCookie('showWheel') === null) {
        setCookie('showWheel', true, 10000);
        $('#wofModal').modal('show');
    }
}

document.querySelector("#mailForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var form = $(this);
    $.ajax({
        url: url,
        type: "POST",
        dataType: 'json',
        data: form.serialize(),
        success: function (result) {
            $('#email').addClass("is-valid").removeClass('is-invalid');
            spin(result.code);
        },
        error: function (xhr, resp, text) {
            if (xhr.responseJSON.status === 'invalid-mail') {
                $('#email').addClass("is-invalid");
            }
        }
    });
});

setTimeout(function () {
    console.log("Show now!");
    displayWheel()
}, 5000);