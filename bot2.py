import os
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import data  # import the data.py file
from telegram.ext import ConversationHandler



TELEGRAM_API_TOKEN = "6048464902:AAGqfTO4cTHjfttuvK_V2TUuySZTkimLBp8"
DATA_FILE = "countries.json"


def load_countries():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_countries(countries_dict):
    with open(DATA_FILE, "w") as file:
        json.dump(countries_dict, file)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a category and country name, and I will add it to the list.")


valid_categories = ["ethnic_conflicts", "anti_government_clashes", "war", "natural_disasters", "frozen_conflicts", "terrorism"]

def add_country(update: Update, context: CallbackContext):
    country = update.message.text

    # If the provided country name doesn't match any country in data.countries
    if country not in data.countries:
        # Find countries that start with the same two letters
        similar_countries = [c for c in data.countries if c.lower().startswith(country.lower()[:2])]

        if similar_countries:
            suggestions = ", ".join(similar_countries)
            update.message.reply_text(
                f"Country '{country}' is not a valid country name. "
                f"Did you mean one of these? {suggestions}"
            )
        else:
            update.message.reply_text(f"Country '{country}' is not a valid country name.")
        return

    context.user_data['pending_country'] = country
    categories_text = "\n".join(f"{i + 1}. {category}" for i, category in enumerate(valid_categories))
    update.message.reply_text(f"Select a category for '{country}' by entering its number:\n\n{categories_text}")
    return 1


def category_selected(update: Update, context: CallbackContext):
    category_number = update.message.text
    if not category_number.isdigit() or int(category_number) not in range(1, len(valid_categories) + 1):
        update.message.reply_text("Invalid input. Please enter a valid category number.")
        return

    category = valid_categories[int(category_number) - 1]
    country = context.user_data['pending_country']
    del context.user_data['pending_country']

    countries_dict = load_countries()
    if country not in countries_dict[category]:
        countries_dict[category].append(country)
        save_countries(countries_dict)
        update.message.reply_text(f"Country '{country}' added to the {category} category.")
    else:
        update.message.reply_text(f"Country '{country}' is already in the {category} category.")
    return -1  # This is a state identifier for the ConversationHandler we'll add later


def show_countries(update: Update, context: CallbackContext):
    if not context.args:
        categories_text = "\n".join(f"{i + 1}. {category}" for i, category in enumerate(valid_categories))
        update.message.reply_text(f"Select a category by entering its number:\n\n{categories_text}")
        return 1  # This is a state identifier for the ConversationHandler we'll add later

def show_selected_category(update: Update, context: CallbackContext):
    category_number = update.message.text
    if not category_number.isdigit() or int(category_number) not in range(1, len(valid_categories) + 1):
        update.message.reply_text("Invalid input. Please enter a valid category number.")
        return

    category = valid_categories[int(category_number) - 1]
    countries_list = load_countries()[category]
    countries_text = "\n".join(countries_list)
    if not countries_list:
        update.message.reply_text(f"There are no countries in the {category} category.")
    else:
        update.message.reply_text(f"Countries in the {category} category:\n\n{countries_text}")
    return -1  # This is a state identifier for the ConversationHandler we'll add later



def remove_country(update: Update, context: CallbackContext):
    categories_text = "\n".join(f"{i + 1}. {category}" for i, category in enumerate(valid_categories))
    update.message.reply_text(f"Select a category by entering its number:\n\n{categories_text}")
    return 1  # This is a state identifier for the ConversationHandler we'll add later


def category_for_removal_selected(update: Update, context: CallbackContext):
    category_number = update.message.text
    if not category_number.isdigit() or int(category_number) not in range(1, len(valid_categories) + 1):
        update.message.reply_text("Invalid input. Please enter a valid category number.")
        return

    category = valid_categories[int(category_number) - 1]
    context.user_data['selected_category'] = category
    countries_list = load_countries()[category]
    countries_text = "\n".join(countries_list)

    if not countries_list:
        update.message.reply_text(f"There are no countries in the {category} category.")
        return -1  # This is a state identifier for the ConversationHandler we'll add later

    update.message.reply_text(
        f"Countries in the {category} category:\n\n{countries_text}\n\nEnter the country name you want to remove:")
    return 2  # This is a state identifier for the ConversationHandler we'll add later

def remove_country_from_selected_category(update: Update, context: CallbackContext):
    country = update.message.text
    category = context.user_data['selected_category']
    del context.user_data['selected_category']

    countries_dict = load_countries()
    if country in countries_dict[category]:
        countries_dict[category].remove(country)
        save_countries(countries_dict)
        update.message.reply_text(f"Country '{country}' removed from the {category} category.")
    else:
        update.message.reply_text(f"Country '{country}' not found in the {category} category.")
    return -1  # This is a state identifier for the ConversationHandler we'll add later


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    remove_country_handler = ConversationHandler(
        entry_points=[CommandHandler("remove", remove_country)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, category_for_removal_selected)],
            2: [MessageHandler(Filters.text & ~Filters.command, remove_country_from_selected_category)]
        },
        fallbacks=[],
        map_to_parent={-1: ConversationHandler.END}
    )
    dispatcher.add_handler(remove_country_handler)

    show_countries_handler = ConversationHandler(
        entry_points=[CommandHandler("show", show_countries)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, show_selected_category)]
        },
        fallbacks=[],
        map_to_parent={-1: ConversationHandler.END}
    )
    dispatcher.add_handler(show_countries_handler)

    add_country_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, add_country)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, category_selected)],
        },
        fallbacks=[],
        map_to_parent={-1: ConversationHandler.END}
    )
    dispatcher.add_handler(add_country_handler)

    updater.start_polling(timeout=30)

if __name__ == '__main__':
    main()



