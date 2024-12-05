import React from "react";
import HeroTask from "./HeroTask";

interface InitiationHeroTasksProps {
  tasks: {
    imageUrl: string;
    backgroundImage: string;
    title: string;
    description: string;
    buttonText: string;
    buttonUrl: string;
    bgImageAlt: string;
   
  }[];
}

const InitiationHeroTasks: React.FC<InitiationHeroTasksProps> = ({ tasks }) => {
  return (
    <div className="flex flex-wrap justify-center gap-8 max-w-full overflow-hidden">
      {tasks.map((task, index) => (
        <div key={index} className="flex-shrink  ">
          <HeroTask
          backgroundImage={task.backgroundImage}
            imageUrl={task.imageUrl}
            title={task.title}
            description={task.description}
            buttonText={task.buttonText}
            buttonUrl={task.buttonUrl}
            alt={task.bgImageAlt}
           
          />
        </div>
      ))}
    </div>
  );
};

export default InitiationHeroTasks;
