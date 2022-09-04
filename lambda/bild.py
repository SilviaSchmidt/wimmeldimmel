# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from json_funcs import read_json
from function import check_location, check_farbe, check_special


from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])



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

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
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
        if not attr["counter"] > 0:
            speak_output = "Du hast keine Versuche mehr."
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
        
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
        h_location = 0
        h_farbe = 0
        h_special = 0

        for objekt in data:
            location_counter = check_location(location, data[objekt]['locations'])
            farbe_counter = check_farbe(farbe, data[objekt]['farbe'])
            special_counter = check_special(special, data[objekt]['special'])

            final_counter = location_counter + farbe_counter

            if highest_object < final_counter:
                object_name = objekt
                highest_object = final_counter
                h_location = location_counter
                h_farbe = farbe_counter
                h_special = special_counter
            
        if highest_object:
            speak_output = "Es funktioniert! {} {} h_location: {} h_farbe: {} h_special: {} special: {}, farbe: {}, location: {}. Ist das korrekt? ".format(object_name, highest_object, h_location, h_farbe, h_special, special, farbe, location)
        else:
            speak_output = "Soso, du meinst also object_name: {} final_counter: {} rest: {} {} {} ".format(object_name, final_counter, special, farbe, location)


        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
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
        if attr["counter"] > 0:
            speak_output = "Dann lass uns loslegen! Was soll ich für dich finden?"
        else:
            speak_output = "Du hast leider keine Versuche mehr übrig."
        
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
                .ask(speak_output)
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
            speak_output = """Wähle zuerst ein Objekt und bitte mich mithilfe einer kurzen Beschreibung, dieses zu finden. xxxBEISPIELxxx? 
                            Ich werde dir dann das gesuchte Objekt markieren, damit du mir sagen kannst, ob es sich um dieses handelt. 
                            Am Ende kannst du noch ein Feedback zum Wimmelbildspiel geben. Dann lass uns loslegen! Was soll ich für dich finden?"""
        elif attr["state"] == "GameIntent":
            speak_output = "Schade, dann versuche ich es nochmal, einen Moment bitte. XXX ANPASSEN"
        elif attr["state"] == "NewGameIntent":
            speak_output = "Danke, dass wir zusammen wimmeln durften. Bis zum nächsten Mal!"
        else:
            speak_output = "Hä?"
        

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
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


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
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

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


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
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()