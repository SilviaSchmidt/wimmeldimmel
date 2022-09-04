# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_supported_interfaces
from json_funcs import read_json, replace_pic
from function import check_location, check_farbe, check_special
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand, AutoPageCommand, HighlightMode

from ask_sdk_model import Response

def load_apl_doc(file_path):
    """Load apl files as dict object"""
    with open(file_path) as f: 
        return json.load(f) 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

quest = "First"


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        speak_output = "Soso, du möchtest also wimmeln. Weißt du wie man wimmelt?"
        # save attributes
        
        attributes_manager = handler_input.attributes_manager
        state_attribute = {
            "state": "LaunchRequest",
            "counter": 3
        }
        attributes_manager.persistent_attributes = state_attribute
        attributes_manager.save_persistent_attributes()

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=load_apl_doc("visuals/wimmel_apl.json")
                                )
                            )
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )

class NewGameIntentHandler(AbstractRequestHandler):
    """Handler for New Game."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("NewGameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        speak_output = "Super! Ich weiß alles! Möchtest du nochmal spielen?"
        # save attributes
        attributes_manager = handler_input.attributes_manager
        state_attribute = {
            "state": "NewGameIntent",
            "counter": 3
        }
        attributes_manager.persistent_attributes = state_attribute
        attributes_manager.save_persistent_attributes()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GameIntentHandler(AbstractRequestHandler):
    """Handler for GameIntent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        if attr["counter"] == 0:
            attr["counter"] = 3
        
        curr_counter = attr["counter"] - 1
        
        attributes_manager = handler_input.attributes_manager
        state_attribute = {
            "state": "GameIntent",
            "counter": curr_counter
        }
        
        attributes_manager.persistent_attributes = state_attribute
        attributes_manager.save_persistent_attributes()

        slots = handler_input.request_envelope.request.intent.slots
        special = slots["object"].value
        farbe = slots["farbe"].value
        location = slots["location"].value
        
        data = read_json()

        highest_object = 0
        object_name = ''

        for objekt in data:
            final_counter = 0
            if location:
                location_counter = check_location(location, data[objekt]['locations'])
                final_counter += location_counter
            if farbe:
                farbe_counter = check_farbe(farbe, data[objekt]['farbe'])
                final_counter += farbe_counter
            if special:
                special_counter = check_special(special, data[objekt]['special'])
                final_counter += special_counter

            if highest_object < final_counter:
                object_name = objekt
                highest_object = final_counter

        speak_output = "Hast du dieses Objekt gemeint?"


        return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=load_apl_doc("objects/{}.json".format(object_name))
                                )
                            )
                    .response
            )


class PreGameIntentHandler(AbstractRequestHandler):
    """Handler for PreGameIntent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PreGameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        speak_output = "Legen wir los! Was soll ich für dich finden?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # retrieve attributes
        attr = handler_input.attributes_manager.persistent_attributes
        if attr["state"] == "LaunchRequest":
            return PreGameIntentHandler().handle(handler_input)
        elif attr["state"] == "GameIntent":
            return NewGameIntentHandler().handle(handler_input)
        elif attr["state"] == "NewGameIntent":
            speak_output = "Was soll ich für dich finden?"
        else:
            speak_output = "Hä?"

        return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=load_apl_doc("visuals/wimmel_apl.json")
                                )
                            )
                    .response
            )

class NoIntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # retrieve attributes
        attr = handler_input.attributes_manager.persistent_attributes
        if attr["state"] == "LaunchRequest":
            speak_output = """Wähle zuerst ein Objekt und bitte mich mithilfe einer kurzen Beschreibung, dieses zu finden. Zum Beispiel: Der runde blaue Globus in der Mitte. Oder: Gelbes fliegendes Objekt.
                            Ich werde dir dann das gesuchte Objekt markieren, damit du mir sagen kannst, ob es sich um dieses handelt. 
                            Am Ende kannst du noch ein Feedback zum Wimmelbildspiel geben. Dann lass uns loslegen! Was soll ich für dich finden?"""
        elif attr["state"] == "GameIntent" and attr["counter"] == 2:
            speak_output = "Schade, lass es mich nochmal versuchen. Bitte gib mir eine genauere Beschreibung."
        elif attr["state"] == "GameIntent" and attr["counter"] == 1:
            speak_output = "Hmm, das ist echt schwierig! Aber einen Versuch habe ich noch. Was genau soll ich nochmal finden?"
        elif attr["state"] == "GameIntent" and attr["counter"] == 0:
            speak_output = "Wie schade! Leider finde ich dein gesuchtes Objekt nicht. Bitte beschreibe mir ein anderes!"   
        elif attr["state"] == "NewGameIntent":
            speak_output = "Danke, dass wir zusammen wimmeln durften. Möchtest du ein Feedback geben oder möchtest du das Spiel beenden?"
        else:
            speak_output = "Hä?"
        

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class FeedbackIntentHandler(AbstractRequestHandler):
    """Handler for Feedback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FeedbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global quest
        slots = handler_input.request_envelope.request.intent.slots
        q1 = slots["first"].value
        q2 = slots["second"].value
        q3 = slots["third"].value
        q4 = slots["forth"].value
        
        if quest == "First":
            speak_output = "Wie gefällt dir das Wimmelbild? sehr, geht so, gar nicht"
            quest = "Second"
        elif quest == "Second":
            if q1 == "sehr":
                speak_output = "Das freut mich, dass dir das Bild gefällt! Wie zufrieden bist du mit meinen Fundergebnissen? sehr zufrieden, zufrieden, unzufrieden, sehr unzufrieden "
            elif q1 == "geht so":
                "Ok, verstehe. Wie zufrieden bist du mit meinen Fundergebnissen? sehr zufrieden, zufrieden, unzufrieden, sehr unzufrieden "
            elif q1 == "gar nicht":
                speak_output = "Wie schade, dass es dir nicht gefällt! Wie zufrieden bist du mit meinen Fundergebnissen? sehr zufrieden, zufrieden, unzufrieden, sehr unzufrieden "
            
            quest = "Third"
            
        elif quest == "Third":
            if q2 == "sehr zufrieden" or q2 == "zufrieden":
                speak_output = "Das macht mich glücklich! Wieviel Freude hat es dir bereitet mit mir zu spielen? sehr viel, viel, ein wenig, gar keine"
            elif q2 == "sehr unzufrieden" or q2 == "unzufrieden":
                speak_output = "Oh, das tut mir leid. Wieviel Freude hat es dir bereitet mit mir zu spielen? sehr viel, viel, ein wenig, gar keine "
            
            quest = "Forth"
        
        elif quest == "Forth":
            if q3 == "sehr viel" or q3 == "viel":
                speak_output = "Es hat mir auch Freude bereitet mit dir zu spielen! Hier noch eine letzte Frage: Wievielen Freunden wirst du mich weiterempfehlen zum Wimmeln? mehr als fünf, weniger als fünf, einem, keinem "
            elif q3 == "ein wenig" or q3 == "gar keine":
                speak_output = "Oh, jetzt bin etwas traurig. Hier noch eine letzte Frage: Wievielen Freunden wirst du mich weiterempfehlen zum Wimmeln? mehr als fünf, weniger als fünf, einem, keinem "

            quest = "Fifth"

        elif quest == "Fifth":
            if q4 == "mehr als fünf" or q4 == "weniger als fünf":
                speak_output = "Juhuu ich freue mich schon darauf mit deinen Freunden zu spielen! Danke schön für dein Feedback und bis zum nächsten Mal!"
            elif q4 == "einem":
                speak_output = "Juhuu ich freue mich schon darauf mit deinem Freund zu spielen! Danke schön für dein Feedback und bis zum nächsten Mal!"
            elif q4 == "keinem":
                speak_output = "Oh, wie schade, ich hoffe, dass du bald trotzdem noch mal mit mir spielst. Danke schön für dein Feedback und bis zum nächsten Mal!"
            else:
                speak_output = "Juhuu ich freue mich schon darauf mit deinen Freunden zu spielen! Danke schön für dein Feedback und bis zum nächsten Mal!"

            quest = "First"

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=load_apl_doc("visuals/goodbye_apl.json")
                                )
                            )
                    .response
            )

        else:
            speak_output = "Danke schön für dein Feedback und bis zum nächsten Mal!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class SpielBeendenIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SpielBeendenIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Tschüss und bis zum nächsten Mal."

        return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=load_apl_doc("visuals/goodbye_apl.json")
                                )
                            )
                    .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Cancel Stop Intent"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

sb.add_request_handler(NewGameIntentHandler())
sb.add_request_handler(PreGameIntentHandler())
sb.add_request_handler(GameIntentHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(SpielBeendenIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(FeedbackIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()