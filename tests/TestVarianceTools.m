classdef TestVarianceTools < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function dvar4varxReturnsSaneCovariance(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 450, 'seed', 10, 'noiseStd', 0.03);

            f = 5;
            p = 10;

            [~, ~, VARX, ~, Zps] = testutils.callDordvarxFull(u, y, f, p);

            [P, sigma] = dvar4varx(u, y, p, VARX, Zps);

            % sigma should be l-by-l (SISO => 1x1) and positive
            testCase.verifySize(sigma, [1 1]);
            testCase.verifyTrue(isfinite(sigma));
            testCase.verifyGreaterThan(sigma, 0);

            % P should be square and finite
            testCase.verifyEqual(size(P,1), size(P,2));
            testCase.verifyTrue(all(isfinite(P(:))));

            % P should be (approximately) symmetric
            symErr = norm(P - P', 'fro') / max(1, norm(P, 'fro'));
            testCase.verifyLessThan(symErr, 1e-8);

            % P should be (approximately) PSD, allow tiny negative due to numerics
            e = eig((P + P')/2);
            testCase.verifyGreaterThan(min(e), -1e-8);
        end

        function dvar4varxbatchRunsAndMatchesDimensions(testCase)
            N = 450;
            f = 5;
            p = 10;

            % Two batches with same length
            [u1, y1] = testutils.makeSisoData('N', N, 'seed', 11, 'noiseStd', 0.03);
            [u2, y2] = testutils.makeSisoData('N', N, 'seed', 12, 'noiseStd', 0.05);
        
            [~, ~, VARX, ~, Zps] = testutils.callDordvarxFull(u1, y1, f, p);

            [Pbatch, sigmabatch] = dvar4varxbatch({u1, u2}, {y1, y2}, p, VARX, Zps);

            testCase.verifyEqual(size(Pbatch,1), size(Pbatch,2));
            testCase.verifyTrue(all(isfinite(Pbatch(:))));
            testCase.verifySize(sigmabatch, [1 1]);
            testCase.verifyGreaterThan(sigmabatch, 0);
        end

        function dvar2frdRunsOnVarxCovariance(testCase)
            [u, y, ~] = testutils.makeSisoData('N', 500, 'seed', 13, 'noiseStd', 0.03);

            f = 5;
            p = 10;

            [~, ~, VARX, ~, Zps] = testutils.callDordvarxFull(u, y, f, p);
            [P, ~] = dvar4varx(u, y, p, VARX, Zps);

            % Frequencies in rad/s for discrete-time with sample time h = 1
            w = linspace(0, pi, 16);
            h = 1;

            [G, covG] = dvar2frd(P, w, h, p, VARX);

            % For SISO: G is 1-by-(r+l)-by-Nw, r=1 l=1 so 1x2xNw
            testCase.verifySize(G, [1 2 numel(w)]);
            testCase.verifyTrue(all(isfinite(G(:))));

            % covG is l-by-(r+l)-by-Nw-by-2-by-2 => 1x2xNw x2x2
            testCase.verifySize(covG, [1 2 numel(w) 2 2]);
            testCase.verifyTrue(all(isfinite(covG(:))));

            % Diagonal covariance terms should be nonnegative (allow tiny negatives)
            diag11 = squeeze(covG(1,1,:,1,1));
            testCase.verifyGreaterThan(min(diag11), -1e-10);
        end

        function dvar2eigMatchesScalarCase(testCase)
            % For n = 1, eigenvalue is A, and covariance should map directly.
            A = 0.7;
            P = 1e-4; % variance of A

            [E, covE] = dvar2eig(P, A);

            testCase.verifyEqual(E, A, 'AbsTol', 1e-12);
            testCase.verifySize(covE, [2 2]);

            % covE(1,1) should be about P, imag part has ~0 variance
            testCase.verifyEqual(covE(1,1), P, 'RelTol', 1e-2);
            testCase.verifyLessThan(abs(covE(2,2)), 1e-8);
        end
    end
end