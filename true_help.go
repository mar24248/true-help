package main

import (
	"github.com/hypermodeinc/modus/sdk/go/pkg/models"
	"github.com/hypermodeinc/modus/sdk/go/pkg/models/openai"
	"fmt"
	"os"
)

const modelName = "text-generator"

func ExtractKnowledgeGraph(text string) (string, error) {
	model, err := models.GetModel[openai.ChatModel](modelName)
	if err != nil {
		return "", err
	}

	// Create system and user messages with clear instructions
	systemPrompt := `You are a knowledge graph extraction system. Analyze the provided text and:
1. Identify key entities (people, organizations, concepts, etc.)
2. Extract relationships between these entities
3. Format the output as a structured list of relationships in the format:
   ENTITY1 -> RELATIONSHIP -> ENTITY2`

	input, err := model.CreateInput(
		openai.NewSystemMessage(systemPrompt),
		openai.NewUserMessage(text),
	)
	if err != nil {
		return "", err
	}

	// Set parameters for more deterministic output
	input.Temperature = 0.3
	input.MaxTokens = 1000

	output, err := model.Invoke(input)
	if err != nil {
		return "", err
	}

	return output.Choices[0].Message.Content, nil
}

func main() {
	// Check if filename is provided
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run true_help.go <filename>")
		os.Exit(1)
	}

	// Read the content from the provided file
	content, err := os.ReadFile(os.Args[1])
	if err != nil {
		panic(err)
	}
	text := string(content)
	
	knowledgeGraph, err := ExtractKnowledgeGraph(text)
	if err != nil {
		panic(err)
	}
	fmt.Println(knowledgeGraph)
}
