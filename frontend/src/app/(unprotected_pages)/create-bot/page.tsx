"use client";
import { useState } from "react";
import ArticleWrapper from "@/_components/_display/ArticleWrapper";
import ToggleButton from "@/_components/_props/ToggleButton";

// Define types for the steps
type Step = {
  type: "simple" | "questionnaire";
  stepText?: string;
  question?: string;
  optionA?: string;
  optionAtext?: string;
  optionB?: string;
  optionBtext?: string;
};

// Define types for the framework
type Framework = {
  name: string;
  ladderRanking: number;
  easeOfUse: number;
  steps: Step[];
};

// Define the structure for languages and frameworks
type LanguageFrameworks = {
  frameworks: Framework[];
};

// Define the complete botFrameworks type
type BotFrameworks = {
  [language: string]: LanguageFrameworks;
};

// Mock data with the new types
const botFrameworks: BotFrameworks = {
  python: {
    frameworks: [
      {
        name: "python-sc2",
        ladderRanking: 1,
        easeOfUse: 1,
        steps: [
          { type: "simple", stepText: "Install Python from python.org" },
          {
            type: "simple",
            stepText: "Install python-sc2 using `pip install python-sc2`",
          },
          {
            type: "questionnaire",
            question: "Choose A or B?",
            optionA: "A",
            optionAtext:
              "You chose A. `Follow the basic tutorial for beginners.`",
            optionB: "B",
            optionBtext:
              "You chose B. Follow the advanced tutorial for experts.",
          },
        ],
      },
      {
        name: "sharpy-sc2",
        ladderRanking: 2,
        easeOfUse: 2,
        steps: [
          { type: "simple", stepText: "Install Python from python.org" },
          {
            type: "simple",
            stepText: "Install sharpy-sc2 using pip install sharpy-sc2",
          },
          {
            type: "simple",
            stepText: "Follow the advanced bot-building tutorial",
          },
        ],
      },
    ],
  },
  cpp: {
    frameworks: [
      {
        name: "cpp-sc2",
        ladderRanking: 3,
        easeOfUse: 1,
        steps: [
          {
            type: "simple",
            stepText: "Install the C++ SC2 API from cpp-sc2.github.io",
          },
          {
            type: "simple",
            stepText: "Set up your bot using the provided template.",
          },
        ],
      },
      {
        name: "commandcenter",
        ladderRanking: 1,
        easeOfUse: 2,
        steps: [
          { type: "simple", stepText: "Install the C++ SC2 API" },
          {
            type: "simple",
            stepText: "Clone the CommandCenter repository and set up the bot.",
          },
        ],
      },
    ],
  },
  java: {
    frameworks: [
      {
        name: "ocraft-s2client",
        ladderRanking: 2,
        easeOfUse: 1,
        steps: [
          {
            type: "simple",
            stepText:
              "Install Java and download the Ocraft-s2client framework.",
          },
          {
            type: "simple",
            stepText: "Build your bot using the starter template.",
          },
        ],
      },
    ],
  },
};

// State types
type Language = "python" | "cpp" | "java" | "Any" | "";
type FrameworkType = "Beginner" | "Ladder" | "";
type QuestionResponses = { [index: number]: string };

const Page = () => {
  const [preferredLanguage, setPreferredLanguage] = useState<Language>("");
  const [frameworkType, setFrameworkType] = useState<FrameworkType>(""); // Beginner or Ladder
  const [selectedFramework, setSelectedFramework] = useState<Framework | null>(
    null
  );
  const [specificFramework, setSpecificFramework] = useState<string>(""); // Track specific framework selection
  const [questionResponses, setQuestionResponses] = useState<QuestionResponses>(
    {}
  ); // Track responses for questionnaire steps

  const handleLanguageSelection = (lang: Language) => {
    setPreferredLanguage(lang);
    setFrameworkType("");
    setSelectedFramework(null);
    setSpecificFramework(""); // Reset everything on language change
  };

  const handleFrameworkTypeSelection = (type: FrameworkType) => {
    setFrameworkType(type);
    const frameworks =
      preferredLanguage === "Any"
        ? getAllFrameworks()
        : botFrameworks[preferredLanguage]?.frameworks || [];
    const filteredFramework = filterFrameworks(frameworks, type);
    setSelectedFramework(filteredFramework);
    setSpecificFramework(""); // Reset dropdown selection
  };

  // Function to filter frameworks based on type (Easiest or Highest Ranked)
  const filterFrameworks = (
    frameworks: Framework[],
    type: FrameworkType
  ): Framework | null => {
    if (type === "Beginner") {
      return frameworks.sort((a, b) => a.easeOfUse - b.easeOfUse)[0]; // Easiest for Beginners
    } else if (type === "Ladder") {
      return frameworks.sort((a, b) => a.ladderRanking - b.ladderRanking)[0]; // Highest Ranked on Ladder
    }
    return null;
  };

  const handleSpecificFrameworkSelection = (framework: string) => {
    const allFrameworks = getAllFrameworks();
    const selected = allFrameworks.find((f) => f.name === framework) || null;
    setSelectedFramework(selected);
    setSpecificFramework(framework); // Set dropdown value
    setFrameworkType(""); // Reset framework type (Beginner/Ladder) if specific is selected
  };

  // Helper function to get all frameworks (for 'None' option or specific selection)
  const getAllFrameworks = (): Framework[] => {
    const allFrameworks: Framework[] = [];
    Object.values(botFrameworks).forEach((language: LanguageFrameworks) => {
      allFrameworks.push(...language.frameworks);
    });
    return allFrameworks;
  };

  const frameworksToDisplay: Framework[] =
    preferredLanguage === "Any"
      ? getAllFrameworks()
      : botFrameworks[preferredLanguage]?.frameworks || [];

  // Handle questionnaire response
  const handleQuestionResponse = (
    stepIndex: number,
    selectedOption: string
  ) => {
    setQuestionResponses((prevResponses) => ({
      ...prevResponses,
      [stepIndex]: selectedOption,
    }));
  };

  const formatStepText = (stepText?: string) => {
    if (!stepText) return null; // Handle undefined or null stepText

    // Split the text by backticks to identify code segments
    const parts = stepText.split(/`(.*?)`/g);

    // Return JSX with code snippets styled appropriately
    return parts.map((part, index) =>
      index % 2 === 1 ? (
        <code
          key={index}
          className="bg-gray-800 text-customGreen px-2 ml-2 py-1 rounded-md font-mono text-base align-middle"
        >
          {part}
        </code>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  return (
    <ArticleWrapper>
      <div className="min-h-screen bg-slate-700 text-gray-200 p-6">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-customGreen">
            AI Arena Bot Builder
          </h1>
          <p className="mt-4 text-lg">
            Start by choosing your preferred language and framework to get a
            personalized bot development tutorial.
          </p>
        </header>

        {/* Step 1: Choose Preferred Language */}
        <section className="mb-12">
          <h2 className="text-3xl font-semibold text-customGreen">
            1. Choose Your Preferred Coding Language
          </h2>
          <div className="flex flex-wrap justify-center space-x-4 mt-4">
            <ToggleButton
              onClick={() => handleLanguageSelection("python")}
              className={`btn ${
                preferredLanguage === "python"
                  ? "bg-customGreen"
                  : "bg-gray-600"
              }`}
              text="Python"
            />

            <ToggleButton
              onClick={() => handleLanguageSelection("cpp")}
              className={`btn ${
                preferredLanguage === "cpp" ? "bg-customGreen" : "bg-gray-600"
              }`}
              text="   C++"
            />

            <ToggleButton
              onClick={() => handleLanguageSelection("java")}
              className={`btn ${
                preferredLanguage === "java" ? "bg-customGreen" : "bg-gray-600"
              }`}
              text="Java"
            />

            <ToggleButton
              onClick={() => handleLanguageSelection("Any")}
              className={`btn ${
                preferredLanguage === "Any" ? "bg-customGreen" : "bg-gray-600"
              }`}
              text="Any"
            />
          </div>
        </section>

        {/* Step 2: Choose Framework Type */}
        {preferredLanguage && (
          <section className="mb-12">
            <h2 className="text-3xl font-semibold text-customGreen">
              2. Choose a Framework
            </h2>
            <div className="flex flex-wrap justify-center space-x-4 mt-4">
              <ToggleButton
                onClick={() => handleFrameworkTypeSelection("Beginner")}
                className={`btn ${
                  frameworkType === "Beginner"
                    ? "bg-customGreen"
                    : "bg-gray-600"
                }`}
                text="Easiest for Beginners"
              />

              <ToggleButton
                onClick={() => handleFrameworkTypeSelection("Ladder")}
                className={`btn ${
                  frameworkType === "Ladder" ? "bg-customGreen" : "bg-gray-600"
                }`}
                text="Highest Ranked on Ladder"
              />
            </div>

            {/* Optional: Specific Framework Dropdown */}
            <div className="mt-6">
              <label htmlFor="framework-select" className="text-lg">
                Or, select a specific framework:
              </label>
              <select
                id="framework-select"
                className={`${
                  specificFramework.length >= 1
                    ? "bg-customGreen "
                    : "bg-gray-600"
                } ml-2 p-2 text-white rounded-md`}
                value={specificFramework} // Display selected framework in dropdown
                onChange={(e) =>
                  handleSpecificFrameworkSelection(e.target.value)
                }
              >
                <option value="">Select Framework</option>
                {frameworksToDisplay.map((framework, index) => (
                  <option key={index} value={framework.name}>
                    {framework.name}
                  </option>
                ))}
              </select>
            </div>
          </section>
        )}
        {/* Step 3: Display Selected Framework */}
        {selectedFramework && (
          <section className="mb-12">
            <h2 className="text-3xl font-semibold text-customGreen">
              3. Getting started with {selectedFramework.name}
            </h2>
            <div className="mt-4 bg-slate-600 p-6 rounded-md shadow-md">
              <ol className="list-decimal list-outside pl-6 mt-4 space-y-6">
                {selectedFramework.steps.map((step, index) => {
                  if (step.type === "simple") {
                    return (
                      <li
                        key={index}
                        className="flex items-start bg-gray-700 p-4 rounded-lg shadow-sm"
                      >
                        <p className="text-lg font-medium ml-2">
                          {formatStepText(step.stepText)}
                        </p>
                      </li>
                    );
                  } else if (step.type === "questionnaire") {
                    const userResponse = questionResponses[index];
                    return (
                      <li
                        key={index}
                        className="flex flex-col bg-gray-700 p-4 rounded-lg shadow-sm"
                      >
                        <p className="flex text-lg font-medium m-2">
                          {step.question}
                        </p>
                        <div className="flex space-x-4 m-2">
                          <ToggleButton
                            text={step.optionA}
                            onClick={() => handleQuestionResponse(index, "A")}
                            className={`btn py-2 px-4 rounded-md transition-all ${
                              userResponse === "A"
                                ? "bg-customGreen border-customGreen text-white"
                                : "bg-gray-600 border-gray-500 text-white hover:border-customGreen hover:text-white"
                            }`}
                          />
                          <ToggleButton
                            onClick={() => handleQuestionResponse(index, "B")}
                            className={`btn py-2 px-4 rounded-md transition-all ${
                              userResponse === "B"
                                ? "bg-customGreen border-customGreen text-white"
                                : "bg-gray-600 border-gray-500 text-white hover:border-customGreen hover:text-white"
                            }`}
                            text={step.optionB}
                          />
                        </div>
                        {userResponse && (
                          <p className="mr-auto text-lg font-medium m-2">
                            {userResponse === "A"
                              ? formatStepText(step.optionAtext)
                              : formatStepText(step.optionBtext)}
                          </p>
                        )}
                      </li>
                    );
                  }
                  return null;
                })}
              </ol>
            </div>
          </section>
        )}
      </div>
    </ArticleWrapper>
  );
};

export default Page;