window.addEventListener("load", () => {
    const select_genres = document.getElementById("js--select-genres");
    const button_whitelist = document.getElementById("button_whitelist");
    const button_blacklist = document.getElementById("button_blacklist");

    const whitelist = document.getElementById("js--whitelist");
    const blacklist = document.getElementById("js--blacklist");
    const search_button = document.getElementById('js--search_button');

    const game_list = document.getElementById("js--games_list");

    var recommended = [];

    function add_whitelist() {
        let value = select_genres.value;
        if (value != "") {
            let element = createGenreElement(value);
            element.onclick = () => remove_filter(value);
            whitelist.append(element);
            setAvailabillity(false, value);
        } else {
            alert("Select a genre")
        }
    }

    function add_blacklist() {
        let value = select_genres.value;
        if (value != "") {
            let element = createGenreElement(value);
            element.onclick = () => remove_filter(value);
            blacklist.append(element);
            setAvailabillity(false, value);
        } else {
            alert("Select a genre");
        }
    }

    function remove_filter(genre_name) {
        let whitelist_tags = whitelist.getElementsByTagName("li");
        for (let x = 0; x < whitelist_tags.length; x++) {
            if (whitelist_tags[x].textContent == genre_name) {
                whitelist_tags[x].remove();
                setAvailabillity(true, genre_name)
                break;
            }
        }

        let blacklist_tags = blacklist.getElementsByTagName("li");
        for (let x = 0; x < blacklist_tags.length; x++) {
            if (blacklist_tags[x].textContent == genre_name) {
                blacklist_tags[x].remove();
                setAvailabillity(true, genre_name)
                break;
            }
        }
    }

    function createGenreElement(genre_name) {
        let element = document.createElement("li");
        element.textContent = genre_name;
        return element;
    }

    function setAvailabillity(visible, genre_name) {
        for (let x = 0; x < select_genres.length; x++) {
            if (select_genres[x].value == genre_name) {

                if (visible) {
                    select_genres[x].removeAttribute("disabled");
                } else {
                    select_genres[x].setAttribute("disabled", "");
                }
                
                select_genres[0].selected = true;
                break;
            }
        }
    }

    function recommendgame() {
        let whitelist_array = ArrayToString([].slice.call(whitelist.getElementsByTagName("li")).map(x => x.textContent));
        let blacklist_array = [].slice.call(blacklist.getElementsByTagName("li")).map(x => x.textContent);
        let parameters;

        if (whitelist_array != "[]") {
            var formData = new FormData();
            formData.append("game_genres", whitelist_array)

            parameters = {
                method: "POST",
                body: formData
            }
        } else {
            parameters = {
                method: "GET"
            }
        }

        fetch("http://127.0.0.1:8000/games", parameters)
        .then((response) => {
            return response.json();
        })
        .then((jsonResponse) => {
            choose_random(jsonResponse, blacklist_array);
        });
    }

    function choose_random(data, blacklist) {
        // Check if there if the first object is an array, is api is giving the object instead of array when using whitelist
        let games = data["games"];
        if (Array.isArray(games[Object.keys(games)[0]])) {
            games = games[Object.keys(games)[0]];
        }

        if (!Array.isArray(games)) {
            alert("No (more) games in this category");
            return;
        }

        // Filter the blacklist && Games already recommended
        let filtered_games = games.map(game => {
            let genres = game["genres"].map(a => a["description"]);
            let hasBlacklist = genres.some(r=> blacklist.includes(r));
            if (!hasBlacklist) return game;
        }).filter(x => x).filter(x => !recommended.includes(x["appid"]));

        if (filtered_games.length == 0) {
            alert("No (more) games in this category");
            return;
        }  

        let random = Math.floor(Math.random() * filtered_games.length);
        let random_game = filtered_games[random];
        recommended.push(random_game["appid"]);
        addtoWebsite(random_game);
    }

    function addtoWebsite(game) {
        let element = create_game_card(game);
        game_list.prepend(element);
        element.style.opacity = 0;
        setTimeout(() => {
            element.style.opacity = 1;
        }, 200)
    }

    function create_game_card(game) {
        let div = document.createElement("div");
        div.setAttribute("class", "games_entry");

        let div_image = document.createElement("div");
        div_image.setAttribute("class", "games_image");
        let image = document.createElement("img");
        image.setAttribute("src", `http://cdn.cloudflare.steamstatic.com/steam/apps/${game["appid"]}/header.jpg`);
        div_image.append(image)

        // Title
        let title = document.createElement("p");
        let title_subject = document.createElement("span");
        title_subject.textContent = "Title";
        title.append(title_subject);
        var game_name = document.createTextNode(game["name"]);
        title.appendChild(game_name);
        
        // Genres
        let genres = document.createElement("p");
        let genres_subject = document.createElement("span");
        genres_subject.textContent = "Genres";
        genres.append(genres_subject);
        let genres_string = game["genres"].map(x => x["description"]).toString().split(",").join(", ");
        var genres_name = document.createTextNode(genres_string);
        genres.appendChild(genres_name);

        // Steam
        let steam = document.createElement("p");
        let steam_subject = document.createElement("span");
        steam_subject.textContent = "Title";
        steam.append(steam_subject);
        let a = document.createElement("a");
        a.textContent = "Link";
        a.setAttribute("href", "https://store.steampowered.com/app/" + game["appid"]);
        a.setAttribute("target", "_blank");
        steam.append(a);

        div.append(div_image);
        div.append(title);
        div.append(genres);
        div.append(steam);

        return div
    }

    function ArrayToString(data) {
        let text = '[';
        for(let x = 0; x < data.length; x++ ) {
            text += '"' + data[x] + '"';
            if (x != data.length -1) {
                text += ", "
            }
        }
        text += ']'
        return text;
    }

    function init() {
        fetch("http://127.0.0.1:8000/genres").then((response) => {
            return response.json();
        })
        .then((jsonResponse) => {
            for (let x = 0; x < jsonResponse["genres"].length; x++) {
                let DOM_option = document.createElement("option");
                DOM_option.setAttribute("value", jsonResponse["genres"][x].description);
                DOM_option.textContent = jsonResponse["genres"][x].description;
                select_genres.append(DOM_option);
            };
        });

        button_whitelist.onclick = () => add_whitelist();
        button_blacklist.onclick = () => add_blacklist();
        search_button.onclick = () => recommendgame();
    }

    init();
})