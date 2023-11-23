# Use the official .NET SDK image for ARM architecture to build the application
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src

# Copy csproj and restore as a distinct layer
COPY ["AquaHub.NConsole/AquaHub.NConsole.csproj", "AquaHub.NConsole/"]
RUN dotnet restore "AquaHub.NConsole/AquaHub.NConsole.csproj"

# Copy the rest of the source code
COPY . .
WORKDIR "/src/AquaHub.NConsole"

# Build the project for ARM
RUN dotnet build "AquaHub.NConsole.csproj" -c Release -o /app/build

# Publish the project for ARM
FROM build AS publish
RUN dotnet publish "AquaHub.NConsole.csproj" -c Release -o /app/publish

# Generate the final image using the official .NET runtime image for ARM
FROM mcr.microsoft.com/dotnet/runtime:7.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Set the command to run the application
ENTRYPOINT ["dotnet", "AquaHub.NConsole.dll"]